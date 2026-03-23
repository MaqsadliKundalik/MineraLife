from django.contrib import admin
from .models import Client, ClientPhoneNumber


class ClientPhoneNumberInline(admin.TabularInline):
    model = ClientPhoneNumber
    extra = 1
    fields = ('phone_number', 'is_primary')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_primary_phone', 'longitude', 'latitude', 'created_at', 'updated_at')
    search_fields = ('name', 'phone_numbers__phone_number')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ClientPhoneNumberInline]
    
    def get_primary_phone(self, obj):
        return obj.get_primary_phone() or "—"
    get_primary_phone.short_description = "Asosiy telefon"


@admin.register(ClientPhoneNumber)
class ClientPhoneNumberAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "client", "is_primary", "created_at")
    list_filter = ("is_primary", "created_at")
    search_fields = ("phone_number", "client__name")