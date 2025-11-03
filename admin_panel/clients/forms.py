# clients/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Client, ClientPhoneNumber


def _attrs(**kw):
    base = {
        "class": "w-full rounded-lg border border-gray-300 dark:border-gray-600 "
                 "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 "
                 "px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
    }
    base.update(kw)
    return base


class ClientPhoneNumberForm(forms.ModelForm):
    """Mijoz telefon raqami formasi"""
    
    class Meta:
        model = ClientPhoneNumber
        fields = ['phone_number', 'description', 'is_primary']
        widgets = {
            'phone_number': forms.TextInput(attrs=_attrs(placeholder="+998901234567")),
            'description': forms.TextInput(attrs=_attrs(placeholder="Kimning raqami?")),
            'is_primary': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].label = "Telefon raqam"
        self.fields['description'].label = "Izoh"
        self.fields['is_primary'].label = "Asosiy raqam"


# Telefon raqamlar uchun inline formset
ClientPhoneNumberFormSet = inlineformset_factory(
    Client, 
    ClientPhoneNumber,
    form=ClientPhoneNumberForm,
    extra=1,  # 1 ta bo'sh form ko'rsatish
    can_delete=True,  # O'chirish imkoniyati
    min_num=0,  # Minimal 0 ta raqam - telefon shart emas
    validate_min=False,  # Min validation o'chirish
    max_num=10,  # Maksimal 10 ta raqam
)

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "latitude", "longitude", "caption"]
        widgets = {
            "name": forms.TextInput(attrs=_attrs(placeholder="Ism Familiya")),
            "latitude": forms.NumberInput(attrs=_attrs(step="0.000001", placeholder="41.311081")),
            "longitude": forms.NumberInput(attrs=_attrs(step="0.000001", placeholder="69.240562")),
            "caption": forms.Textarea(attrs=_attrs(placeholder="Qo'shimcha ma'lumotlar")),
        }

    def clean(self):
        data = super().clean()
        lat, lon = data.get("latitude"), data.get("longitude")
        # Agar bittasi kiritilsa, ikkinchisi ham bo‘lsin
        if (lat is None) ^ (lon is None):
            raise forms.ValidationError("Latitude va Longitude ikkalasi ham birga kiritilishi kerak (yoki ikkalasi ham bo‘sh).")
        # Diapazon tekshiruvi
        if lat is not None and not (-90 <= lat <= 90):
            self.add_error("latitude", "Latitude -90 dan 90 gacha bo‘lishi kerak.")
        if lon is not None and not (-180 <= lon <= 180):
            self.add_error("longitude", "Longitude -180 dan 180 gacha bo‘lishi kerak.")
        return data
