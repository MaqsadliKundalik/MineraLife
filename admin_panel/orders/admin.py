from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'status', 'created_at')  # Removed 'product' as it is not a valid field
    search_fields = ('client__name', 'product__name', 'status')  # Ensure related fields exist in Client and Product models
    list_filter = ('status',)
