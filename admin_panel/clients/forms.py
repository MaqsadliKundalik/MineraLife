# clients/forms.py
from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "phone_number", "latitude", "longitude"]
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Ism Familiya",
                "class": "w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            }),
            "phone_number": forms.TextInput(attrs={
                "placeholder": "+998 90 123 45 67",
                "class": "w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            }),
            "latitude": forms.NumberInput(attrs={
                "step": "0.000001",
                "placeholder": "41.311081",
                "class": "w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            }),
            "longitude": forms.NumberInput(attrs={
                "step": "0.000001",
                "placeholder": "69.240562",
                "class": "w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            }),
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
