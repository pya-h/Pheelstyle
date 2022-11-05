from django.shortcuts import render
from store.models import Product, Review


def home(request):
    popular_products = Product.objects.all().filter(available=True).order_by('-created')

    for product in popular_products:
        reviews = Review.objects.filter(product_id=product.id, status=True)
    context = {
        'popular_products': popular_products,
        'reviews': reviews
    }
    return render(request, 'index.html', context)
