from django.views.generic import ListView
from .models import Client
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView
from django.contrib import messages
from .models import Client
from .forms import ClientForm, ClientPhoneNumberFormSet
from admin_panel.mixins import SuperuserRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from django.db.models import Max
from django.utils import timezone
import json

class ClientListView(SuperuserRequiredMixin, ListView):
    model = Client
    template_name = 'clients/clients_list.html'
    context_object_name = 'clients'
    paginate_by = 12  # har sahifada nechta yozuv
    ordering = '-created_at'  # xohlasangiz
    
    def get_queryset(self):
        return Client.objects.prefetch_related('phone_numbers').order_by(self.ordering)

class ClientCreateView(SuperuserRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"
    success_url = reverse_lazy("clients:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['phone_formset'] = ClientPhoneNumberFormSet(self.request.POST)
        else:
            context['phone_formset'] = ClientPhoneNumberFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        phone_formset = context['phone_formset']
        
        with transaction.atomic():
            if phone_formset.is_valid():
                # Kamida bitta telefon raqam bo'lishi kerak
                valid_phones = [f for f in phone_formset.forms if f.cleaned_data and not f.cleaned_data.get('DELETE')]
                if not valid_phones:
                    messages.error(self.request, "Kamida bitta telefon raqam kiritish shart!")
                    return self.render_to_response(self.get_context_data(form=form))
                
                self.object = form.save()
                phone_formset.instance = self.object
                phone_formset.save()
                messages.success(self.request, "Mijoz muvaffaqiyatli qo'shildi.")
                return super().form_valid(form)
            else:
                return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, "Formada xatolar bor. Iltimos, tekshirib qayta yuboring.")
        return super().form_invalid(form)

class ClientDetailView(SuperuserRequiredMixin, DetailView):
    model = Client
    template_name = "clients/client_detail.html"
    context_object_name = "client"
    
    def get_queryset(self):
        return Client.objects.prefetch_related('phone_numbers')

class ClientDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Client
    template_name = "clients/client_confirm_delete.html"
    context_object_name = "client"
    success_url = reverse_lazy("clients:list")

class ClientUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"
    context_object_name = "client"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['phone_formset'] = ClientPhoneNumberFormSet(self.request.POST, instance=self.object)
        else:
            context['phone_formset'] = ClientPhoneNumberFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        phone_formset = context['phone_formset']
        
        with transaction.atomic():
            if phone_formset.is_valid():
                # Kamida bitta telefon raqam bo'lishi kerak
                valid_phones = [f for f in phone_formset.forms if f.cleaned_data and not f.cleaned_data.get('DELETE')]
                if not valid_phones:
                    messages.error(self.request, "Kamida bitta telefon raqam kiritish shart!")
                    return self.render_to_response(self.get_context_data(form=form))
                
                self.object = form.save()
                phone_formset.instance = self.object
                phone_formset.save()
                messages.success(self.request, "Mijoz ma'lumotlari yangilandi.")
                return super().form_valid(form)
            else:
                return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy("clients:detail", kwargs={"pk": self.object.pk})


@require_http_methods(["GET"])
def check_name_exists(request):
    """AJAX endpoint to check if client name already exists"""
    name = request.GET.get('name', '').strip()
    client_id = request.GET.get('client_id', None)
    
    if not name:
        return JsonResponse({'exists': False})
    
    # Check if name exists
    query = Client.objects.filter(name__iexact=name)
    
    # If updating existing client, exclude current client from check
    if client_id:
        query = query.exclude(pk=client_id)
    
    exists = query.exists()
    
    return JsonResponse({'exists': exists, 'name': name})


@login_required
def clients_map(request):
    """Barcha mijozlarni xaritada ko'rsatish"""
    # Oxirgi buyurtma sanasini annotate qilish
    clients = Client.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).prefetch_related('phone_numbers').annotate(
        last_order_date=Max('orders__effective_date')
    )
    
    points = [{
        "id": c.id,
        "name": c.name,
        "phone": c.get_phone_numbers_display(),
        "caption": c.caption or "",
        "lat": c.latitude,
        "lon": c.longitude,
        "last_order_date": c.last_order_date.isoformat() if c.last_order_date else None,
    } for c in clients]
    
    return render(request, "clients/clients_map.html", {
        "points": json.dumps(points),
        "total_clients": clients.count(),
        "yandex_maps_api_key": settings.YANDEX_MAPS_API_KEY,
    })
