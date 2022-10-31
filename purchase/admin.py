from django.contrib import admin
from .models import Transaction, Order, PurchasedItem, OrderReceiver

# TODO:
# ADD TRANSACTION & ORDERRECEIVER MANAGERS CLASSES AS INLINES FOR ORDER ADMIN PANEL


class PurchasedItemInline(admin.TabularInline):
    model = PurchasedItem
    readonly_fields = ('product', 'order', 'buyer', 'quantity', 'cost', 'color', 'size', 'delivered')
    extra = 0


class OrderReceiverInline(admin.TabularInline):
    model = OrderReceiver
    readonly_fields = ('related_to', 'fname', 'lname', 'province', 'city', 'phone', 'address', 'postal_code')  # , 'order')
    extra = 0


class OrderAdminPanel(admin.ModelAdmin):
    list_display = ('key', 'buyer', 'status', 'date_updated', )  # 'is_certified', 'is_delivered', )
    list_filter = ('status', )  # 'is_certified', 'is_delivered')
    search_fields = ('key', 'status')
    list_per_page = 20
    inlines = (PurchasedItemInline,)  # OrderReceiverInline)


class PurchasedItemAdminPanel(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'product', 'quantity', 'date_created', )  # 'is_certified', 'is_delivered', )
    list_per_page = 20


class OrderReceiverAdminPanel(admin.ModelAdmin):
    list_display = ('id', 'fname', 'lname', 'province', 'city')
    list_per_page = 20


admin.site.register(Transaction)
admin.site.register(Order, OrderAdminPanel)
admin.site.register(PurchasedItem, PurchasedItemAdminPanel)
admin.site.register(OrderReceiver, OrderReceiverAdminPanel)
