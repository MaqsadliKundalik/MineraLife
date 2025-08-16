# orders/forms.py
from django import forms
from django.contrib.auth.models import User, Group
from .models import Order

def courier_qs():
    g = Group.objects.filter(name="couriers").first()
    if not g:
        return User.objects.none()
    return User.objects.filter(groups=g, is_active=True).order_by('username')

def _attrs(**kw):
    base = {
        "class": "w-full rounded-lg border border-gray-300 dark:border-gray-600 "
                 "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 "
                 "px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
    }
    base.update(kw); return base

class OrderForm(forms.ModelForm):
    courier = forms.ModelChoiceField(
        queryset=courier_qs(),
        required=False,                    # xohlasangiz True qilib majburiy qiling
        empty_label="— Kurer tanlanmagan —",
        widget=forms.Select(attrs={
            "class": "w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 "
                     "text-gray-900 dark:text-gray-100 px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
        })
    )

    class Meta:
        model = Order
        fields = ["client", "courier", "quantity", "price", "status", "effective_date", "notes"]
        widgets = {
            "client": forms.Select(attrs=_attrs()),
            "quantity": forms.NumberInput(attrs=_attrs(min=1)),
            "price": forms.NumberInput(attrs=_attrs(step="0.01")),
            "status": forms.Select(attrs=_attrs()),
            "effective_date": forms.DateInput(attrs=_attrs(type="date")),
            "notes": forms.Textarea(attrs=_attrs(rows=3)),
        }

def _attrs(**kw):
    base = {
        "class": "w-full rounded-lg border border-gray-300 dark:border-gray-600 "
                 "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 "
                 "px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
    }
    base.update(kw); return base
