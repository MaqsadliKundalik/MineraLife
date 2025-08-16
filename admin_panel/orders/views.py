from django.views.generic import ListView, CreateView, DetailView, TemplateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Prefetch
from .models import Order
from .forms import OrderForm
from django.utils import timezone
from django.utils.dateparse import parse_date
from datetime import timedelta
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.generic import TemplateView
from django.contrib.auth.models import User, Group
from admin_panel.mixins import SuperuserRequiredMixin

class OrderListView(SuperuserRequiredMixin, ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 12
    ordering = "-created_at"

    # --- Sana parsing: bir nechta formatni qo‘llab-quvvatlaydi ---
    def _parse_date_safe(self, s: str | None):
        """
        YYYY-MM-DD (standart), MM/DD/YYYY yoki DD/MM/YYYY ko‘rinishlarini qabul qiladi.
        Brauzer/locale turlicha yuborganda ham ishlashi uchun.
        """
        if not s:
            return None
        # 1) standart (YYYY-MM-DD)
        d = parse_date(s)
        if d:
            return d
        # 2) muqobil formatlar
        for fmt in ("%m/%d/%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None

    # --- GET dan oraliqni aniqlash + preset ---
    def _get_date_range(self):
        today = timezone.localdate()
        preset = (self.request.GET.get("preset") or "").lower()

        # Preset ustun (kecha/bugun/ertaga)
        if preset in {"yesterday", "today", "tomorrow"}:
            if preset == "yesterday":
                start = end = today - timedelta(days=1)
            elif preset == "tomorrow":
                start = end = today + timedelta(days=1)
            else:
                start = end = today
            return start, end, preset

        # Qo‘lda kiritilgan start/end
        start = self._parse_date_safe(self.request.GET.get("start_date"))
        end   = self._parse_date_safe(self.request.GET.get("end_date"))

        # Default: bugun
        if not start and not end:
            start = end = today

        # Bittasi yo‘q bo‘lsa ikkinchisiga teng
        if start and not end:
            end = start
        if end and not start:
            start = end

        # Noto‘g‘ri tartib bo‘lsa almashtiramiz
        if start and end and end < start:
            start, end = end, start

        # Agar aynan bitta kun bo‘lsa, avtomatik preset nomini ham qaytaramiz
        auto_preset = ""
        if start and end and start == end:
            if start == today:
                auto_preset = "today"
            elif start == today - timedelta(days=1):
                auto_preset = "yesterday"
            elif start == today + timedelta(days=1):
                auto_preset = "tomorrow"

        return start, end, auto_preset

    # --- Asosiy queryset: sana oraliq bo‘yicha filtrlash ---
    def get_queryset(self):
        qs = (Order.objects
              .select_related("client")
              .order_by("-created_at"))

        start, end, _ = self._get_date_range()
        if start and end:
            qs = qs.filter(effective_date__range=(start, end))
        return qs

    # --- Template context ---
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        start, end, preset = self._get_date_range()
        today = timezone.localdate()
        ctx.update({
            "start_date": start,
            "end_date": end,
            "preset": preset,                     # tugmalarda “aktiv” ko‘rsatish uchun
            "today": today,
            "yesterday": today - timedelta(days=1),
            "tomorrow": today + timedelta(days=1),
        })

        # Mini xarita: shu oraliqqa tushgan, koordinatasi bor buyurtmalar (50 taga cheklaymiz)
        map_qs = (self.get_queryset()
                  .filter(client__latitude__isnull=False,
                          client__longitude__isnull=False)
                  .order_by("-created_at")[:50])

        ctx["map_points"] = [
            {
                "id": o.id,
                "client": o.client.name,
                "lat": o.client.latitude,
                "lon": o.client.longitude,
                "status": o.get_status_display(),
                "price": float(o.price),
                "date": o.effective_date.isoformat(),
            }
            for o in map_qs
        ]
        return ctx


class OrdersMapView(SuperuserRequiredMixin, TemplateView):
    template_name = "orders/order_map.html"

    # --- Sana parsing: bir nechta format ---
    def _parse_date_safe(self, s: str | None):
        if not s:
            return None
        d = parse_date(s)  # YYYY-MM-DD
        if d:
            return d
        for fmt in ("%m/%d/%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                pass
        return None

    def _get_date_range(self, request):
        today = timezone.localdate()
        preset = (request.GET.get("preset") or "").lower()

        if preset in {"yesterday", "today", "tomorrow"}:
            if preset == "yesterday":
                start = end = today - timedelta(days=1)
            elif preset == "tomorrow":
                start = end = today + timedelta(days=1)
            else:
                start = end = today
            return start, end, preset

        start = self._parse_date_safe(request.GET.get("start_date"))
        end   = self._parse_date_safe(request.GET.get("end_date"))

        if not start and not end:
            start = end = today
        if start and not end:
            end = start
        if end and not start:
            start = end
        if start and end and end < start:
            start, end = end, start

        auto = ""
        if start == end:
            if start == today:
                auto = "today"
            elif start == today - timedelta(days=1):
                auto = "yesterday"
            elif start == today + timedelta(days=1):
                auto = "tomorrow"

        return start, end, auto or preset

    def _courier_qs(self):
        g = Group.objects.filter(name="couriers").first()
        if not g:
            return User.objects.none()
        return User.objects.filter(groups=g, is_active=True).order_by("username")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        req = self.request

        # Sana oraliq
        start, end, preset = self._get_date_range(req)

        # Kurer filtri (bir yoki ko‘p qiymat)
        selected_ids = []
        if "courier" in req.GET:
            # ?courier=1&courier=3 kabi
            try:
                selected_ids = [int(x) for x in req.GET.getlist("courier") if x.strip()]
            except ValueError:
                selected_ids = []

        qs = (Order.objects
              .select_related("client", "courier")
              .filter(client__latitude__isnull=False,
                      client__longitude__isnull=False,
                      effective_date__range=(start, end))
              .order_by("-created_at"))

        if selected_ids:
            qs = qs.filter(courier_id__in=selected_ids)

        ctx["points"] = [
            {
                "id": o.id,
                "client": o.client.name,
                "lat": o.client.latitude,
                "lon": o.client.longitude,
                "status": o.get_status_display(),
                "price": float(o.price),
                "date": o.effective_date.isoformat(),
                "courier": (o.courier.username if o.courier_id else None),
            }
            for o in qs
        ]

        ctx["start_date"] = start
        ctx["end_date"] = end
        ctx["preset"] = preset
        ctx["couriers"] = list(self._courier_qs().values("id", "username"))
        ctx["selected_couriers"] = selected_ids
        return ctx


class OrderCreateView(SuperuserRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/order_form.html"
    success_url = reverse_lazy("orders:list")


class OrderDetailView(SuperuserRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

class OrderUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/order_form.html"
    context_object_name = "order"

    def get_success_url(self):
        # Yangilangan buyurtmaning detail sahifasiga qaytamiz
        return reverse_lazy("orders:detail", kwargs={"pk": self.object.pk})


class OrderDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Order
    template_name = "orders/order_confirm_delete.html"
    context_object_name = "order"
    success_url = reverse_lazy("orders:list")
