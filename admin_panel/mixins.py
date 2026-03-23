# core/mixins.py
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = getattr(settings, "LOGIN_URL", "/admin/login/")

    def test_func(self):
        return self.request.user.is_superuser
