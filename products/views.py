from django.shortcuts import render
from .models import Product
from django.views import View
from django.utils import timezone
from admin_panel.mixins import SuperuserRequiredMixin

# Create your views here.
class ProductListView(SuperuserRequiredMixin, View):
    def get(self, request):
        products = Product.objects.all()
        return render(request, 'products/products_list.html', {'products': products, "now": timezone.now()})

class ProductDetailView(SuperuserRequiredMixin, View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        return render(request, 'products/product_detail.html', {'product': product})