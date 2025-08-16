from django.urls import path
from .views import (
    OrderDeleteView, OrderListView, OrderCreateView, OrderDetailView, OrderUpdateView, OrdersMapView, 
)

app_name = "orders"

urlpatterns = [
    path("", OrderListView.as_view(), name="list"),
    path("create/", OrderCreateView.as_view(), name="create"),
    path("map/", OrdersMapView.as_view(), name="map"),
    path("<int:pk>/", OrderDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", OrderUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", OrderDeleteView.as_view(), name="delete"),
]
