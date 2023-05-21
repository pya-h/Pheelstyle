from django.contrib import admin
from .models import Transaction, Order, PurchasedItem, OrderReceiver
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from common.tools import MailingInterface
from devshare.models import DevShare

# TODO:
# ADD TRANSACTION & ORDERRECEIVER MANAGERS CLASSES AS INLINES FOR ORDER ADMIN PANEL


class PurchasedItemInline(admin.TabularInline):
    model = PurchasedItem

    readonly_fields = ('product', 'variation', 'order', 'buyer', 'quantity', 'cost', 'delivered')
    fields = ('product', 'variation', 'quantity', 'cost')
    extra = 0


class OrderReceiverInline(admin.TabularInline):
    model = OrderReceiver
    readonly_fields = ('related_to', 'fname', 'lname', 'province', 'city', 'phone', 'address', 'postal_code')  # , 'order')
    extra = 0


class OrderAdminPanel(admin.ModelAdmin):
    list_display = ('key', 'buyer', 'status', 'seen',)
    list_filter = ('status', 'seen', )
    search_fields = ('key', 'status')
    list_per_page = 20
    inlines = (PurchasedItemInline,)  # OrderReceiverInline)
    change_form_template = "personalization/order_admin_template.html"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        order = get_object_or_404(Order, id=object_id)
        order.seen = True
        order.save()
        return super().change_view(request=request, object_id=object_id, form_url='', extra_context=None)

    def response_change(self, request, obj):
        try:
            if "btn_verify_order" in request.POST:
                order = get_object_or_404(Order, id=obj.id, key=obj.key)
                if order.status != "verified" and order.status != 'sent' and order.status != "delivered":
                    order.status = "verified"
                    order.seen = True
                    goods = PurchasedItem.objects.filter(order=order)

                    for item in goods:
                        item.variation.stock -= item.quantity
                        item.variation.save()
                        item.save()

                    order.whats_wrong = None
                    # send email with details to notify that the order is verified and will be prepared to send
                    if not order.buyer or not order.buyer.email:
                        messages.error(request, "خریدار این سفارش و یا ایمیل وی مشخص نیست. احتمالا اطلاعات این کاربر دستکاری شده است و نیاز به بررسی دارد.")
                        return redirect(request.path)
                    ref_id = order.transaction.receipt.reference_id if order.transaction and order.transaction.receipt else None
                    MailingInterface.SendMessage(request, order.buyer.email, "تایید سفارش", "order_verified", {"name": order.buyer.fname, "order_key": order.key, "reference_id": ref_id})
                    order.save()
                    try:
                        dev_share = DevShare.objects.get(order=order)
                        dev_share.verify()
                        dev_share.save()
                    except Exception as ex:
                        print("Cannot retrieve developer share: ", ex)
                else:
                    messages.info(request, "این سفارش قبلا تایید شده است.")
                    return redirect(request.path)
            elif "btn_cancel_order" in request.POST:
                cause = request.POST["whats_wrong"]
                if not cause:
                    messages.error(request, "علت رد سفارش را وارد کن.")
                    return redirect(request.path)

                order = get_object_or_404(Order, id=obj.id, key=obj.key)
                order.whats_wrong = cause
                order.seen = True
                order.save()
                if not order.buyer or not order.buyer.email:
                    messages.error(request, "خریدار این سفارش و یا ایمیل وی مشخص نیست. احتمالا اطلاعات این کاربر دستکاری شده است و نیاز به بررسی دارد.")
                    return redirect(request.path)

                MailingInterface.SendMessage(request,
                                             target_email=order.buyer.email,
                                             subject="سفارش نامعتبر",
                                             template_name="order_refused",
                                             dict_content={"name": order.buyer.fname,
                                                           "order_key": order.key,
                                                           "whats_wrong": cause})
                # send email to notify
                # change order status
                # or remove the order?
            elif "btn_indebt" in request.POST:
                pass
            #  COMPLETE THIS IF
        except Exception as ex:
            print("Something went wrong while verifying the order: ", ex)
        return super().response_change(request, obj)


class PurchasedItemAdminPanel(admin.ModelAdmin):
    list_display = ('buyer', 'product', 'variation', 'quantity',)  # 'is_certified', 'is_delivered', )
    list_per_page = 20


class OrderReceiverAdminPanel(admin.ModelAdmin):
    list_display = ('phone', 'fname', 'lname', 'province', 'city')
    list_per_page = 20


admin.site.register(Transaction)
admin.site.register(Order, OrderAdminPanel)
admin.site.register(PurchasedItem, PurchasedItemAdminPanel)
admin.site.register(OrderReceiver, OrderReceiverAdminPanel)
