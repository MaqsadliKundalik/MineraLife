from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "courier", "effective_date", "status", "payment_method", "price", "created_at")
    list_filter = ("status", "payment_method", "effective_date", "courier")
    search_fields = ("client__name", "courier__username", "notes")
