from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Stack, TakenProduct
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .utlities import open_stack, have_same_variations


def submit_preferred_variation(preferred_variations, taken=None, product=None, current_stack=None):
    if len(preferred_variations) == len(Variation.variation_parameters):
        if not taken:
            if product and current_stack:
                taken = TakenProduct.objects.create(product=product, stack=current_stack)
            elif not product:
                raise TakenProduct.DoesNotExist('Unknown product. cannot create a new Taken field')
            elif not current_stack:
                raise Stack.DoesNotExist('Something went wrong while opening a new shopping stack.')
        taken.quantity = 1
        taken.preferred_variations.clear()
        for key in preferred_variations:
            taken.preferred_variations.add(key)
        taken.update_exact_stock()
        taken.save()
    else:
        raise Variation.DoesNotExist('Insufficient number of selected variations')


def put_back(request, product_id, taken_item_id):
    product = get_object_or_404(Product, id=product_id)
    current_stack = None
    try:
        current_stack = open_stack(request)
        taken = TakenProduct.objects.get(id=taken_item_id, product=product, stack=current_stack)
        taken.decrease_quantity()
        taken.save()

    except TakenProduct.DoesNotExist:
        # handle this error (actually it must never happen
        # WRITE A METHOD TO CALCULATE COST CORRECTLY
        pass
    except ObjectDoesNotExist:
        pass
    return redirect("stack")


def put_all(request, product_id, taken_item_id, ):
    product = get_object_or_404(Product, id=product_id)
    current_stack = None
    try:
        current_stack = open_stack(request)
        TakenProduct.objects.get(id=taken_item_id, product=product, stack=current_stack).delete()

    except TakenProduct.DoesNotExist:
        # handle this error (actually it must never happen
        # WRITE A METHOD TO CALCULATE COST CORRECTLY
        pass
    except ObjectDoesNotExist:
        pass
    return redirect("stack")


def take_another(request, product_id, taken_item_id):
    product = Product.objects.get(id=product_id)
    current_stack = None
    try:
        current_stack = open_stack(request)
        taken = TakenProduct.objects.get(id=taken_item_id, product=product, stack=current_stack)
        taken.increase_quantity()
        taken.save()
    except TakenProduct.DoesNotExist:
        taken = TakenProduct.objects.create(product=product, stack=current_stack, quantity=1, total_price=product.price)
        taken.save()
    except ObjectDoesNotExist:
        # handle this error seriously
        pass
    return redirect("stack")


def take_product(request, product_id):
    product = Product.objects.get(id=product_id)

    if request.method == 'POST':
        # collect all the user selection on product variation
        preferred_variations = []
        for key in request.POST:
            value = request.POST[key]
            try:
                preferred = Variation.objects.get(product=product, parameter__iexact=key, value__iexact=value)
                preferred_variations.append(preferred)
            except:  # such as csrf_token
                pass

        current_stack = None
        try:
            current_stack = open_stack(request)
            similar_takens = TakenProduct.objects.filter(product=product, stack=current_stack)
            taken = None
            # count the similar variations

            for similar_taken in similar_takens:
                items_variations = similar_taken.preferred_variations.all()

                if have_same_variations(first=list(items_variations), second=preferred_variations):  # the exact item with exact variations exists in previous stack products
                    # so no need to add new product variations
                    taken = similar_taken
                    break

            if (not taken or not taken.quantity) and product.available:
                submit_preferred_variation(taken=taken, preferred_variations=preferred_variations, product=product, current_stack=current_stack)
            else:
                # SHOW ERROR MESSAGE
                return redirect('stack')
        except TakenProduct.DoesNotExist:
            # handle this error (actually it must never happen
            submit_preferred_variation(preferred_variations=preferred_variations, product=product, current_stack=current_stack)

        except ObjectDoesNotExist:
            # handle this error seriously
            pass
        # handle all errors
    return redirect('stack')


def stack(request):
    try:
        context = open_stack(request).submit_bill()
    except ObjectDoesNotExist:
        # meaning stack does not exist
        context = {
            'taken_products': [],
            'stack': None,
        }
    return render(request, 'store/stack.html', context)


@login_required(login_url='login')
def checkout(request):
    try:
        context = open_stack(request).submit_bill()
    except ObjectDoesNotExist:
        # meaning stack does not exist
        context = {
            'taken_products': [],
            'stack': None,
        }
    return render(request, 'store/checkout.html', context)
