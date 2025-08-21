from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, FormView, UpdateView, DeleteView
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .forms import CourierUserCreateForm, CourierUserUpdateForm, CourierUserPasswordForm, COURIER_GROUP_NAME
from admin_panel.mixins import SuperuserRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from orders.models import Order
from django.db.models import Sum
from django.shortcuts import render
from django.utils.timezone import localdate
# couriers/views.py
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime

from orders.models import Order

def _safe_parse_date(s: str):
    """YYYY-MM-DD ni date ga parse qiladi; xato bo‘lsa None qaytaradi."""
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None

@login_required
def courier_dashboard(request):
    today = localdate()
    qs = (Order.objects
          .select_related("client", "courier")
          .filter(
              courier=request.user,
              effective_date=today
          )
          .order_by("-created_at"))

    cash_total = qs.filter(status="completed", payment_method="cash").aggregate(total=Sum("price"))["total"] or 0
    card_total = qs.filter(status="completed", payment_method="card").aggregate(total=Sum("price"))["total"] or 0
    perechesleniya_total = qs.filter(status="completed", payment_method="perechesleniya").aggregate(total=Sum("price"))["total"] or 0   # 🔹 yangi

    return render(request, "couriers/dashboard.html", {
        "orders": qs,
        "cash_total": cash_total,
        "card_total": card_total,
        "perechesleniya_total": perechesleniya_total,   # 🔹 context ga qo‘shdik
        "today": today,
    })

@login_required
def courier_order_update(request, pk):
    order = get_object_or_404(Order, pk=pk, courier=request.user)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["completed", "cancelled"]:
            order.status = new_status
            order.save()
            messages.success(request, "Buyurtma yangilandi!")
        return redirect("couriers:dashboard")

    return render(request, "couriers/order_detail.html", {"order": order})

@login_required
def courier_map(request):
    today = localdate()
    qs = (Order.objects
          .select_related("client", "courier")
          .filter(
              courier=request.user,
              effective_date=today,
              client__latitude__isnull=False,
              client__longitude__isnull=False
          )
          .order_by("-created_at"))

    points = [{
        "id": o.id,
        "client": o.client.name,
        "phone": o.client.phone_number or "",
        "lat": o.client.latitude,
        "lon": o.client.longitude,
        "status": o.get_status_display(),
        "status_raw": o.status,  # ('pending'...'completed'...'cancelled')
        "quantity": o.quantity,
        "price": float(o.price),
        "date": o.effective_date.isoformat(),
        "payment": "💳 Karta" if o.payment_method == "card" else "💵 Naqd" if o.payment_method == "cash" else "🏦 Perechesleniya",
        "payment_raw": o.payment_method,  # ('card'|'cash')
    } for o in qs]

    stats = {
        "cash": qs.filter(status="completed", payment_method="cash").aggregate(total=Sum("price"))["total"] or 0,
        "card": qs.filter(status="completed", payment_method="card").aggregate(total=Sum("price"))["total"] or 0,
        "perechesleniya": qs.filter(status="completed", payment_method="perechesleniya").aggregate(total=Sum("price"))["total"] or 0,  # 🔹 yangi
    }

    return render(request, "couriers/map.html", {
        "points": points,
        "stats": stats,
        "today": today,
    })


class StaffOnly(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

def _courier_qs():
    group, _ = Group.objects.get_or_create(name=COURIER_GROUP_NAME)
    return User.objects.filter(groups=group).order_by("-date_joined")

class CourierListView(SuperuserRequiredMixin, ListView):
    template_name = "couriers/courier_list.html"
    context_object_name = "couriers"
    paginate_by = 12
    def get_queryset(self):
        return _courier_qs()

class CourierDetailView(SuperuserRequiredMixin, DetailView):
    template_name = "couriers/courier_detail.html"
    context_object_name = "courier"
    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs["pk"], id__in=_courier_qs().values_list("id", flat=True))

class CourierCreateView(SuperuserRequiredMixin, FormView):
    template_name = "couriers/courier_form.html"
    form_class = CourierUserCreateForm
    success_url = reverse_lazy("couriers:list")
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class CourierUpdateView(SuperuserRequiredMixin, UpdateView):
    model = User
    form_class = CourierUserUpdateForm
    template_name = "couriers/courier_form.html"
    context_object_name = "courier"
    def get_queryset(self):
        return _courier_qs()
    def get_success_url(self):
        return reverse_lazy("couriers:detail", kwargs={"pk": self.object.pk})

class CourierPasswordUpdateView(SuperuserRequiredMixin, FormView):
    template_name = "couriers/courier_password.html"
    form_class = CourierUserPasswordForm
    def dispatch(self, request, *args, **kwargs):
        self.courier = get_object_or_404(User, pk=kwargs["pk"], id__in=_courier_qs().values_list("id", flat=True))
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        self.courier.set_password(form.cleaned_data["password1"])
        self.courier.save()
        return redirect("couriers:detail", pk=self.courier.pk)
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["courier"] = self.courier
        return ctx

class CourierDeleteView(SuperuserRequiredMixin, DeleteView):
    template_name = "couriers/courier_confirm_delete.html"
    context_object_name = "courier"
    success_url = reverse_lazy("couriers:list")
    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs["pk"], id__in=_courier_qs().values_list("id", flat=True))
