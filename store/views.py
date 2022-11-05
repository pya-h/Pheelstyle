from django.shortcuts import render, get_object_or_404, redirect
from category.models import Category
from .models import Product, Review, Gallery
from .forms import ReviewForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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
        reviews = Review.objects.filter(product=this_product, status=True)
        #for review in reviews:
            #review.comment = review.comment.replace('\n', ' <br> ')
        gallery = Gallery.objects.filter(product=this_product)
        context = {
            'this_product': this_product,
            'reviews': reviews,
            'gallery': gallery
        }
    except Exception as ex:
        # handle this seriously
        raise ex

    return render(request, 'store/product.html', context)


@login_required(login_url='login')
def post_review(request, product_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                old_review = Review.objects.get(user__id=request.user.id, product__id=product_id)
                form = ReviewForm(request.POST, instance=old_review)  # instance=review parameter will prevent from
                # django from creating new review, and it will replace existing one
                form.save()
                messages.info(request, "نظر قبلی شما به روز رسانی شد.")
            except Review.DoesNotExist:
                form = ReviewForm(request.POST)
                if form.is_valid():
                    try:
                        product_to_be_reviewed = Product.objects.get(id=product_id)
                        new_review = Review(product=product_to_be_reviewed, user=request.user,
                                            comment=form.cleaned_data['comment'], rating=form.cleaned_data['rating'],
                                            ip=request.META.get('REMOTE_ADDR'))
                        # validate form and ip first
                        new_review.save()
                        messages.success(request, 'نظر شما ثبت شد.')
                    except Product.DoesNotExist:
                        messages.error(request, 'شما در حال نظر دادن در رابطه با کالایی هستید که وجود خارجی ندارد!')
    else:
        messages.error(request, 'لطفا اول برادریتو ثابت کن و تو اکانت لاگین کن. بعدش نظر بده.')
    return redirect(request.META.get('HTTP_REFERER'))


