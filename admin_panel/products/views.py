from django.shortcuts import render
from .models import Product
from django.views import View
from django.utils import timezone


# Create your views here.
class ProductListView(View):
    def get(self, request):
        products = Product.objects.all()
        return render(request, 'products/products_list.html', {'products': products, "now": timezone.now()})

class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        return render(request, 'products/product_detail.html', {'product': product})