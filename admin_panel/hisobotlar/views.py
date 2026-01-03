from django.shortcuts import render
from django.db.models import Sum, F, Count, Avg, Q
from django.utils.timezone import now
from django.core.paginator import Paginator
from datetime import timedelta, date
from collections import defaultdict
from orders.models import Order
import json

def reports_view(request):
    # Foydalanuvchi filterini olish
    today = now().date()
    start = request.GET.get("start")
    end = request.GET.get("end")
    quick = request.GET.get("quick", "month")  # default = hozirgi oy
    page_num = request.GET.get("page", 1)

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

    # Asosiy queryset - select_related bilan optimizatsiya
    qs = Order.objects.filter(
        effective_date__range=[start_date, end_date],
        status="completed"  # faqat tugagan buyurtmalar
    ).select_related("client", "courier")

    # === UMUMIY STATISTIKA ===
    # To'lovlar bo'yicha hisoblash
    cash_total = qs.filter(payment_method="cash").aggregate(total=Sum(F("price") * F("outquantity")))["total"] or 0
    card_total = qs.filter(payment_method="card").aggregate(total=Sum(F("price") * F("outquantity")))["total"] or 0
    pereches_total = qs.filter(payment_method="perechesleniya").aggregate(total=Sum(F("price") * F("outquantity")))["total"] or 0
    debt_total = qs.filter(payment_method="debt").aggregate(total=Sum(F("price") * F("outquantity")))["total"] or 0
    total = cash_total + card_total + pereches_total + debt_total

    # Umumiy buyurtmalar soni va o'rtacha narx
    total_orders = qs.count()
    avg_order_value = qs.aggregate(avg=Avg(F("price") * F("outquantity")))["avg"] or 0
    
    # Jami sotilgan mahsulotlar miqdori
    total_sold = qs.aggregate(total=Sum("outquantity"))["total"] or 0
    total_received = qs.aggregate(total=Sum("inquantity"))["total"] or 0

    # === KUNLIK SAVDO DINAMIKASI (chiziqli diagramma uchun) ===
    daily_sales = defaultdict(lambda: {"revenue": 0, "orders": 0, "quantity": 0})
    
    for order in qs.values("effective_date").annotate(
        revenue=Sum(F("price") * F("outquantity")),
        orders_count=Count("id"),
        quantity=Sum("outquantity")
    ).order_by("effective_date"):
        date_str = order["effective_date"].strftime("%Y-%m-%d")
        daily_sales[date_str] = {
            "revenue": float(order["revenue"] or 0),
            "orders": order["orders_count"],
            "quantity": order["quantity"] or 0
        }
    
    # Sanalarni to'ldirish (bo'sh kunlar uchun)
    current = start_date
    chart_labels = []
    chart_revenue = []
    chart_orders = []
    chart_quantity = []
    
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        chart_labels.append(date_str)
        chart_revenue.append(daily_sales[date_str]["revenue"])
        chart_orders.append(daily_sales[date_str]["orders"])
        chart_quantity.append(daily_sales[date_str]["quantity"])
        current += timedelta(days=1)

    # === KURYERLAR BO'YICHA STATISTIKA ===
    courier_stats = (
        qs.values("courier__id", "courier__username")
        .annotate(
            total_revenue=Sum(F("price") * F("outquantity")),
            total_orders=Count("id"),
            total_quantity=Sum("outquantity"),
            avg_order=Avg(F("price") * F("outquantity"))
        )
        .order_by("-total_revenue")
    )

    # === MIJOZLAR BO'YICHA STATISTIKA (pagination bilan) ===
    clients_summary = (
        qs.values("client__id", "client__name", "client__caption")
        .annotate(
            total_revenue=Sum(F("price") * F("outquantity")),
            total_orders=Count("id"),
            total_quantity=Sum("outquantity"),
            avg_order=Avg(F("price") * F("outquantity"))
        )
        .order_by("-total_revenue")
    )
    
    # Pagination
    paginator = Paginator(clients_summary, 50)  # Har sahifada 50 ta mijoz
    clients_page = paginator.get_page(page_num)

    # Mijozga qaysi kur'er xizmat qilganini olish (faqat ko'rinayotgan mijozlar uchun)
    client_ids = [c["client__id"] for c in clients_page]
    client_couriers = {}
    for order in qs.filter(client_id__in=client_ids).select_related("client", "courier"):
        if order.client_id not in client_couriers:
            client_couriers[order.client_id] = order.courier

    # === TOP MIJOZLAR (eng ko'p daromad keltirgan 10 ta) ===
    top_clients = clients_summary[:10]

    return render(request, "hisobotlar/reports.html", {
        "start_date": start_date,
        "end_date": end_date,
        "quick": quick,
        
        # Umumiy statistika
        "cash_total": cash_total,
        "card_total": card_total,
        "pereches_total": pereches_total,
        "debt_total": debt_total,
        "total": total,
        "total_orders": total_orders,
        "avg_order_value": avg_order_value,
        "total_sold": total_sold,
        "total_received": total_received,
        
        # Diagramma ma'lumotlari
        "chart_labels": json.dumps(chart_labels),
        "chart_revenue": json.dumps(chart_revenue),
        "chart_orders": json.dumps(chart_orders),
        "chart_quantity": json.dumps(chart_quantity),
        
        # Kuryerlar statistikasi
        "courier_stats": courier_stats,
        
        # Mijozlar (pagination bilan)
        "clients_page": clients_page,
        "client_couriers": client_couriers,
        
        # Top mijozlar
        "top_clients": top_clients,
    })
