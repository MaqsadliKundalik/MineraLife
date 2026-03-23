from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

@user_passes_test(lambda u: u.is_superuser)
def admin_welcome(request):
    return render(request, "admin_welcome.html")

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_redirect(request):
    if request.user.is_superuser:
        return redirect('admin_welcome')   # admin uchun
    else:
        return redirect('couriers:dashboard')  # kuryer uchun
