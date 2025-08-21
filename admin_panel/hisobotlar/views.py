from django.shortcuts import render
from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta, date
from orders.models import Order

def reports_view(request):
    # Foydalanuvchi filterini olish
    today = now().date()
    start = request.GET.get("start")
    end = request.GET.get("end")
    quick = request.GET.get("quick", "month")  # default = hozirgi oy

    if quick == "month":
        start_date = today.replace(day=1)
        end_date = today
    elif quick == "6months":
        start_date = today - timedelta(days=180)
        end_date = today
    elif quick == "year":
        start_date = today - timedelta(days=365)
        end_date = today
    else:
        try:
            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)
        except Exception:
            start_date = today.replace(day=1)
            end_date = today

    qs = Order.objects.filter(
        effective_date__range=[start_date, end_date],
        status="completed"  # faqat tugagan buyurtmalar
    )

    # To‘lovlar bo‘yicha hisoblash
    cash_total = qs.filter(payment_method="cash").aggregate(total=Sum("price"))["total"] or 0
    card_total = qs.filter(payment_method="card").aggregate(total=Sum("price"))["total"] or 0
    pereches_total = qs.filter(payment_method="perechesleniya").aggregate(total=Sum("price"))["total"] or 0
    total = cash_total + card_total + pereches_total

    # Mijozlar bo‘yicha guruhlash
    clients_summary = (
        qs.values("client__id", "client__name")
        .annotate(total=Sum("price"))
        .order_by("-total")
    )

    # Mijozga qaysi kur'er xizmat qilganini olish
    client_couriers = {}
    for order in qs.select_related("client", "courier"):
        if order.client_id not in client_couriers:
            client_couriers[order.client_id] = order.courier  # faqat bittasini olish

    return render(request, "hisobotlar/reports.html", {
        "start_date": start_date,
        "end_date": end_date,
        "cash_total": cash_total,
        "card_total": card_total,
        "pereches_total": pereches_total,
        "total": total,
        "clients_summary": clients_summary,
        "client_couriers": client_couriers,
        "quick": quick,
    })
