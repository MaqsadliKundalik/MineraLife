from django.contrib import admin
from django import forms
from .models import CourierRoute


class CourierRouteAdminForm(forms.ModelForm):
    """Rang tanlash uchun maxsus form"""
    COLOR_CHOICES = [
        ('#2563eb', '🔵 Ko\'k (Standart)'),
        ('#dc2626', '🔴 Qizil'),
        ('#16a34a', '🟢 Yashil'),
        ('#ca8a04', '🟡 Sariq'),
        ('#9333ea', '🟣 Binafsha'),
        ('#ea580c', '🟠 To\'q sariq'),
        ('#0891b2', '🔵 Moviy'),
        ('#e11d48', '🌸 Pushti'),
    ]
    
    color = forms.ChoiceField(
        choices=COLOR_CHOICES,
        widget=forms.Select(attrs={'class': 'color-select'}),
        label="Marshrut rangi",
        help_text="Xaritada marshrutning rangini tanlang"
    )
    
    class Meta:
        model = CourierRoute
        fields = '__all__'
        widgets = {
            'route_data': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Marshrut koordinatalari JSON formatda: [[lat1, lon1], [lat2, lon2], ...]',
                'class': 'vLargeTextField'
            }),
        }


@admin.register(CourierRoute)
class CourierRouteAdmin(admin.ModelAdmin):
    form = CourierRouteAdminForm
    list_display = ('courier', 'date', 'color_preview', 'created_at', 'updated_at')
    list_filter = ('date', 'courier')
    search_fields = ('courier__username',)
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('courier', 'date', 'color')
        }),
        ('Marshrut', {
            'fields': ('route_data',),
            'description': 'Marshrut koordinatalari JSON formatda kiritiladi. Misol: [[41.2995, 69.2401], [41.3111, 69.2797]]'
        }),
    )
    
    def color_preview(self, obj):
        """Rangni ko'rsatish"""
        return f'<div style="width: 30px; height: 20px; background-color: {obj.color}; border: 1px solid #ccc; border-radius: 3px;"></div>'
    color_preview.short_description = 'Rang'
    color_preview.allow_tags = True
    
    class Media:
        css = {
            'all': ('admin/css/courier_route.css',)
        }
        js = ('admin/js/courier_route.js',)
