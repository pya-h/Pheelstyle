from django.contrib import admin
from .models import Transaction, Order, OrderedProduct


class OrderedProductInline(admin.TabularInline):
    model = OrderedProduct
    readonly_fields = ('product', 'order', 'buyer', 'quantity', 'cost', 'color', 'size', 'delivered')
    extra = 0


class OrderAdminPanel(admin.ModelAdmin):
    list_display = ('key', 'receiver', 'buyer', 'status', 'date_updated', )  # 'is_certified', 'is_delivered', )
    list_filter = ('status', )  # 'is_certified', 'is_delivered')
    search_fields = ('key', 'status')
    list_per_page = 20
    inlines = (OrderedProductInline, )


class OrderedProductAdminPanel(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'product', 'quantity', 'date_created', )  # 'is_certified', 'is_delivered', )
    list_per_page = 20


admin.site.register(Transaction)
admin.site.register(Order, OrderAdminPanel)
admin.site.register(OrderedProduct, OrderedProductAdminPanel)
