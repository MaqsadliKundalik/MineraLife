from django.urls import path
from .views import (
    CourierListView, CourierDetailView, CourierCreateView,
    CourierUpdateView, CourierPasswordUpdateView, CourierDeleteView
)

app_name = "couriers"

urlpatterns = [
    path("", CourierListView.as_view(), name="list"),
    path("create/", CourierCreateView.as_view(), name="create"),
    path("<int:pk>/", CourierDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", CourierUpdateView.as_view(), name="update"),
    path("<int:pk>/password/", CourierPasswordUpdateView.as_view(), name="password"),
    path("<int:pk>/delete/", CourierDeleteView.as_view(), name="delete"),
]
