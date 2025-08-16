from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, FormView, UpdateView, DeleteView
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .forms import CourierUserCreateForm, CourierUserUpdateForm, CourierUserPasswordForm, COURIER_GROUP_NAME
from admin_panel.mixins import SuperuserRequiredMixin

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
