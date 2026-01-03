from django.urls import path
from .views import reports_view, export_excel

app_name = "hisobotlar"

urlpatterns = [
    path("", reports_view, name="reports"),
    path("export-excel/", export_excel, name="export_excel"),
]
