from django.contrib import admin
from .models import CourierRoute


@admin.register(CourierRoute)
class CourierRouteAdmin(admin.ModelAdmin):
    list_display = ('courier', 'date', 'color', 'created_at')
    list_filter = ('date', 'courier')
    search_fields = ('courier__username',)
    date_hierarchy = 'date'
