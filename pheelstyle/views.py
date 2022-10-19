from django.shortcuts import render
from store.models import Product


def home(request):
    popular_products = Product.objects.all().filter(available=True)
    context = {
        'popular_products': popular_products
    }
    return render(request, 'index.html', context)
