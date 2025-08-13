from django import forms
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError

COURIER_GROUP_NAME = "couriers"

def _tw(**kw):
    base = {
        "class": "w-full rounded-lg border border-gray-300 dark:border-gray-600 "
                 "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 "
                 "px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
    }
    base.update(kw)
    return base

class CourierUserCreateForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs=_tw(placeholder="damas1")))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=_tw(placeholder="parol")))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=_tw(placeholder="parolni tasdiqlang")))
    is_active = forms.BooleanField(initial=True, required=False, label="Faol (login ishlasin)")

    def clean_username(self):
        u = self.cleaned_data["username"]
        if User.objects.filter(username=u).exists():
            raise ValidationError("Bu login band.")
        return u

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("password1"), data.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Parollar mos emas.")
        return data

    def save(self):
        data = self.cleaned_data
        user = User(username=data["username"], is_active=data.get("is_active", True))
        user.set_password(data["password1"])
        user.save()

        group, _ = Group.objects.get_or_create(name=COURIER_GROUP_NAME)
        user.groups.add(group)
        return user


class CourierUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["is_active"]
        widgets = {
            "is_active": forms.CheckboxInput(attrs={"class": "h-4 w-4 rounded"})
        }


class CourierUserPasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=_tw(placeholder="yangi parol")))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=_tw(placeholder="tasdiqlash")))
    def clean(self):
        data = super().clean()
        if data.get("password1") != data.get("password2"):
            raise ValidationError("Parollar mos emas.")
        return data
