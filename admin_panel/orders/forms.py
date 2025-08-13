from django import forms
from .models import Order

def _attrs(**kw):
    base = {
        "class": "w-full rounded-lg border border-gray-300 dark:border-gray-600 "
                 "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 "
                 "px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
    }
    base.update(kw)
    return base

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["client", "quantity", "price", "status", "effective_date", "notes"]
        widgets = {
            "client": forms.Select(attrs=_attrs()),
            "quantity": forms.NumberInput(attrs=_attrs(placeholder="Masalan: 3", min=1)),
            "price": forms.NumberInput(attrs=_attrs(step="0.01", placeholder="Masalan: 250000")),
            "status": forms.Select(attrs=_attrs()),
            "effective_date": forms.DateInput(attrs=_attrs(type="date")),
            "notes": forms.Textarea(attrs=_attrs(placeholder="Qo‘shimcha izoh...", rows=3)),
        }
