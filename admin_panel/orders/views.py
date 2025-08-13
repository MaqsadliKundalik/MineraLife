from django.views.generic import ListView, CreateView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Prefetch
from .models import Order
from .forms import OrderForm

class OrderListView(ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 12
    ordering = "-created_at"

    def get_queryset(self):
        return (Order.objects
                .select_related("client")
                .order_by("-created_at"))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Mini xarita uchun faqat koordinatasi bor so‘nggi 20 ta buyurtma
        last_with_geo = (Order.objects
                         .select_related("client")
                         .filter(client__latitude__isnull=False, client__longitude__isnull=False)
                         .order_by("-created_at")[:20])
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
            for o in last_with_geo
        ]
        return ctx


class OrdersMapView(TemplateView):
    template_name = "orders/order_map.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # To‘liq xarita: barcha koordinatali buyurtmalar
        orders = (Order.objects
                  .select_related("client")
                  .filter(client__latitude__isnull=False, client__longitude__isnull=False)
                  .order_by("-created_at"))
        ctx["points"] = [
            {
                "id": o.id,
                "client": o.client.name,
                "lat": o.client.latitude,
                "lon": o.client.longitude,
                "status": o.get_status_display(),
                "price": float(o.price),
                "date": o.effective_date.isoformat(),
            }
            for o in orders
        ]
        return ctx


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/order_form.html"
    success_url = reverse_lazy("orders:list")


class OrderDetailView(DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"
