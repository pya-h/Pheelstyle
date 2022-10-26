from django.shortcuts import render, redirect
from stack.models import TakenProduct
from .forms import OrderForm, ReserveTransactionForm
from stack.utlities import open_stack
from .models import Order, OrderReceiver, Transaction, OrderedProduct, Receipt
import datetime
from django.contrib.auth.decorators import login_required


def finalize_order(request, order_key, method, status, reference_id=None, amount=None):
    order = None
    try:
        order = Order.objects.get(buyer=request.user, key=order_key)
        # order.how_much_to_pay()
        if order:
            order.status = status.lower()
            # now we ship the taken product items to ordered product items
            user_stack = open_stack(request)
            user_stack.submit_bill()  # to make sure total products in the stack are billed successfully
            stack_items = TakenProduct.objects.filter(stack=user_stack)
            for item in stack_items:
                ordered_product = OrderedProduct()
                ordered_product.order_id = order.id  # another way of setting an ForeignKey object's value inside a
                # model
                ordered_product.buyer_id = request.user.id
                ordered_product.product_id = item.product_id
                # variations cannot be set like this, it must be set after .save() call
                ordered_product.quantity = item.quantity
                ordered_product.cost = item.total_price()
                ordered_product.delivered = order.status == 'delivered'
                # ordered_product.color = ...?
                # ordered_product.size = ...?
                preferred_variations = item.preferred_variations.all()
                ordered_product.save()
                ordered_product.variations.set(preferred_variations)
                # **** NOTE ****
                # when applying .variations the tutorial goes other idiotic way
                # and does all the unnecessary things there
                # i do that in a wise way that anyone would do
                # but when running anything went wrong check this part again
                if ordered_product.quantity <= ordered_product.exact_stock():
                    # ordered_product.save()

                    # reduce the sold products from variation.stock values
                    # NOTE: i think this type of saving stock numbers is wrong and will cause problems
                    # because there is no association that which size.stock associates with which color.stock

                    # MOVE THIS PIECE OF CODE TO ADMIN VERIFICATION SECTION FOR INCOMING ORDERS
                    # for preferred_variation in preferred_variations:
                    # variation = Variation.objects.get(id=preferred_variation.id)
                    # variation.stock -= ordered_product.quantity
                    # variation.save()
                    # MOVE CODE ABOVE TO ADMIN VERIFICATION SECTION
                    ordered_product.save()
                    item.delete()  # *** CORRECT ???? ***
                else:
                    ordered_product.anything_wrong = "تعداد درخواستی شما از این نوع کالا، بیشتر از موجودی انبار است."
                    order.status = "failed"
            order.save()
            return order
        else:
            print('No order has been found')
    except Exception as ex:
        print(f'sth went wrong while saving the transaction cause: {ex}')
        if order:
            order.save()


@login_required(login_url='login')
def submit_order(request):
    try:
        if not request.user.is_authenticated:
            return redirect('login')

        user = request.user
        user_stack = open_stack(request)
        user_stack.submit_bill()  # to make sure total products in the stack are billed successfully
        stack_items = TakenProduct.objects.filter(stack=user_stack)
        # use stack_items or add a quantity field to stack model?
        if stack_items.count() <= 0:
            return redirect('store')

        if request.method == 'POST':
            form = OrderForm(request.POST)
            if form.is_valid():
                # first get the data posted by user
                order = Order()
                order.receiver = OrderReceiver()
                order.receiver.fname = form.cleaned_data['fname']
                order.receiver.lname = form.cleaned_data['lname']
                order.receiver.phone = form.cleaned_data['phone']
                order.receiver.postal_code = form.cleaned_data['postal_code']
                order.receiver.province = form.cleaned_data['province']
                order.receiver.city = form.cleaned_data['city']
                order.receiver.address = form.cleaned_data['address']
                order.receiver.related_to = user
                order.receiver.save()

                order.notes = form.cleaned_data['notes']
                order.cost = user_stack.cost * 10
                order.discounts = user_stack.discounts
                order.shipping_cost = 50000  # this is for test; ask pouya about this
                order.how_much_to_pay()  # calculate the cose and update the order.must_be_paid
                # update the ip of the user again just to make sure
                order.buyer = user
                order.buyer.ip = request.META.get('REMOTE_ADDR')

                order.buyer.save()
                order.save()  # call save for django to set the id primary key automatically
                # now I generate the order key: the key that that identifies the order for both seller and buyer
                year = int(datetime.date.today().strftime('%Y'))
                month = int(datetime.date.today().strftime('%m'))
                day = int(datetime.date.today().strftime('%d'))
                today = datetime.date(year, month, day)  # construct today's date in proper format and object
                order_key = today.strftime('%Y%m%d') + str(
                    order.id)  # django default primary key: id starts from 1 increasing by one
                order.key = order_key
                order.save()

                # use Order.objects.get to make sure that the order is saved properly and retrievable
                order = Order.objects.get(buyer=request.user, key=order_key)
                context = {
                    'order': order,
                    'goods': stack_items,
                }
                return render(request, 'purchase/preview.html', context)
    except Exception as ex:
        print('sth went wrong while processing the order cause: ' + ex.__str__())

    return redirect('order')


@login_required(login_url='login')
def preview(request):
    return render(request, 'purchase/preview.html')


@login_required(login_url='login')
def check_order(request, order_key):
    order = finalize_order(request=request, order_key=order_key, method='receipt', status='pending')
    if order and order.status.lower() == "pending":
        # now we send the user to transaction page
        context = {"order": order}
        return redirect(order.receipt_url())
        # return render(request, 'purchase/receipt.html', context)
    # sth went wrong: HANDLE ERROR
    return render(request, 'purchase/preview.html')


# ACTUALLY THIS METHOD MUST BE CALLED BY ADIM SIDE
@login_required(login_url="login")
def accept_order(request, order_key):
    if request.user and request.user.is_authenticated and order_key:
        order = Order.objects.get(key=order_key, buyer=request.user)
        if order and order.status.lower() == "certified":
            order.sell_products()
            context = {"order": order}
            return render(request, 'purchase/result.html', context)
            #  saves automatically in function above
    # send proper error


@login_required(login_url='login')
def take_receipt(request, order_key):
    user = request.user
    if user and user.is_authenticated:
        order = Order.objects.get(buyer=user, key=order_key)
        if order:
            context = {'order': order}
            return render(request, 'purchase/receipt.html', context)
    return render(request, 'purchase/receipt.html')


def reserve_order(request):
    if request.method == "POST":
        form = ReserveTransactionForm(request.POST)
        if form.is_valid():
            receipt = Receipt(reference_id=form.cleaned_data['reference_id'], image=form.cleaned_data['image'],
                              amount=form.cleaned_data['amount'])
            receipt.save()
            transaction = Transaction(performer=request.user, method="reserve", validation="pending", receipt=receipt)
            transaction.save()
            order = Order.objects.get(key=form.cleaned_data["order_key"], buyer=request.user)
            if order:
                order.transaction = transaction
                order.save()
            return redirect(order.accept_url())
        return redirect('home')
