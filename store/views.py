from django.shortcuts import render, get_object_or_404
from category.models import Category
from .models import Product


def store(request, category_filter=None):
    try:
        products = Product.objects.all()  # .filter(available=True)
        if category_filter:
            obj_expected_categories = get_object_or_404(Category, slug=category_filter)
            if obj_expected_categories:
                products = products.filter(category=obj_expected_categories)
    except:
        products = []

    context = {
        'products': products,
        'products_count': products.count if products else 0
    }
    return render(request, 'store/store.html', context)


def product(request, category_filter, product_slug=None):
    context = dict()
    try:
        this_product = Product.objects.get(slug=product_slug, category__slug=category_filter)
        context = {
            'this_product': this_product,
        }
    except Exception as ex:
        # handle this seriously
        raise ex

    return render(request, 'store/product.html', context)
