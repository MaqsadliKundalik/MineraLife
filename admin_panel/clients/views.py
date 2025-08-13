from django.views.generic import ListView
from .models import Client
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView
from django.contrib import messages
from .models import Client
from .forms import ClientForm

class ClientListView(ListView):
    model = Client
    template_name = 'clients/clients_list.html'
    context_object_name = 'clients'
    paginate_by = 12  # har sahifada nechta yozuv
    ordering = '-created_at'  # xohlasangiz

class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"
    success_url = reverse_lazy("clients:list")

    def form_valid(self, form):
        messages.success(self.request, "Mijoz muvaffaqiyatli qo‘shildi.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Formada xatolar bor. Iltimos, tekshirib qayta yuboring.")
        return super().form_invalid(form)

class ClientDetailView(DetailView):
    model = Client
    template_name = "clients/client_detail.html"
    context_object_name = "client"

class ClientDeleteView(DeleteView):
    model = Client
    template_name = "clients/client_confirm_delete.html"
    context_object_name = "client"
    success_url = reverse_lazy("clients:list")

class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"  # yaratgan formamizni qayta ishlatamiz
    context_object_name = "client"

    def get_success_url(self):
        messages.success(self.request, "Mijoz ma'lumotlari yangilandi.")
        # Yangilangan mijozning detail sahifasiga qaytamiz (xohlasangiz listga qaytaring)
        return reverse_lazy("clients:detail", kwargs={"pk": self.object.pk})
