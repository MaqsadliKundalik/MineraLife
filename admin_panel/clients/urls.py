# clients/urls.py
from django.urls import path
from .views import ClientListView, ClientCreateView, ClientDetailView, ClientDeleteView, ClientUpdateView, check_name_exists

app_name = 'clients'
urlpatterns = [
    path('', ClientListView.as_view(), name='list'),
    path("create/", ClientCreateView.as_view(), name="create"), 
    path("<int:pk>/", ClientDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", ClientDeleteView.as_view(), name="delete"),
    path("<int:pk>/update/", ClientUpdateView.as_view(), name="update"),
    path('check-name/', check_name_exists, name='check_name'),
]
