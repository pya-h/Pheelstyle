from django.contrib import admin
from .models import Stack, TakenProduct


class TakenProductAdminPanel(admin.ModelAdmin):
    list_display = ('id', 'product',  'stack', 'quantity', 'is_available',)
    list_filter = ('product', 'stack', 'quantity', 'exact_stock', 'is_available', )


class TakenProductInline(admin.TabularInline):
    model = TakenProduct
    extra = 0


class StackAdminPanel(admin.ModelAdmin):
    list_display = ('sid', 'cost', 'created')
    readonly_fields = ('sid', 'created')
    search_fields = ('sid',)
    inlines = (TakenProductInline, )


admin.site.register(Stack, StackAdminPanel)
admin.site.register(TakenProduct, TakenProductAdminPanel)
