from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Stack, TakenProduct
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .utlities import open_stack


def submit_preferred_variation(variation, taken=None, product=None, current_stack=None):
    if variation:
        print("taken found", taken)
        if not taken:
            if product and current_stack:
                taken = TakenProduct.objects.create(product=product, stack=current_stack, variation=variation)
            elif not product:
                raise TakenProduct.DoesNotExist('Unknown product. cannot create a new Taken field')
            elif not current_stack:
                raise Stack.DoesNotExist('Something went wrong while opening a new shopping stack.')
        taken.quantity = 1
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
    variation = None
    if request.method == 'POST':
        # collect all the user selection on product variation
        color = request.POST['color']
        size = request.POST['size']

        try:
            variation = Variation.objects.get(product=product, color=color, size=size)
        except:  # such as csrf_token
            pass

        current_stack = None
        try:
            current_stack = open_stack(request)
            try:
                taken = TakenProduct.objects.get(variation=variation, stack=current_stack)
            except:
                taken = None

            if (not taken or not taken.quantity) and product.available:
                submit_preferred_variation(taken=taken, variation=variation, product=product, current_stack=current_stack)
            else:
                # SHOW ERROR MESSAGE

                return redirect('stack')
        except TakenProduct.DoesNotExist:
            # handle this error (actually it must never happen
            submit_preferred_variation(variation=variation, product=product, current_stack=current_stack)

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
def order(request):
    try:
        context = open_stack(request).submit_bill()
    except ObjectDoesNotExist:
        # meaning stack does not exist
        context = {
            'taken_products': [],
            'stack': None,
        }
    return render(request, 'purchase/order.html', context)
