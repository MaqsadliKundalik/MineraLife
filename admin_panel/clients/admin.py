from django.contrib import admin

from .models import Client

# Register your models here.
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'longitude', 'latitude', 'created_at', 'updated_at')
    search_fields = ('name', 'phone_number')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')