from django import forms
from .models import Order


def _attrs(**kw):
    base = {
        "class": "w-full rounded-lg border border-gray-300 dark:border-gray-600 "
                 "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 "
                 "px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
    }
    base.update(kw); return base

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["client", "courier", "quantity", "price", "status", "effective_date", "payment_method", "notes"]
        widgets = {
            "client": forms.Select(attrs=_attrs()),
            "courier": forms.Select(attrs=_attrs()),
            "quantity": forms.NumberInput(attrs=_attrs(min=1)),
            "price": forms.NumberInput(attrs=_attrs(step="0.01")),
            "status": forms.Select(attrs=_attrs()),
            "effective_date": forms.DateInput(attrs=_attrs(type="date")),
            # YANGI: to'lov usuli (select yoki radio — istakka ko'ra)
            "payment_method": forms.Select(attrs=_attrs()),
            # Agar radio bo'lsin desangiz:
            # "payment_method": forms.RadioSelect(attrs={"class": "space-x-2"}),
            "notes": forms.Textarea(attrs=_attrs(rows=3)),
        }
