from django.contrib import admin
from .models import Transaction, Order, PurchasedItem, OrderReceiver
from django.shortcuts import get_object_or_404

# TODO:
# ADD TRANSACTION & ORDERRECEIVER MANAGERS CLASSES AS INLINES FOR ORDER ADMIN PANEL


class PurchasedItemInline(admin.TabularInline):
    model = PurchasedItem
    readonly_fields = ('product', 'variation', 'order', 'buyer', 'quantity', 'cost', 'delivered')
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

    def change_view(self, request, object_id, form_url='', extra_context=None):
        order = get_object_or_404(Order, id=object_id)
        order.seen = True
        order.save()
        return super().change_view(request=request, object_id=object_id, form_url='', extra_context=None)


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
