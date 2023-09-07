from django.contrib import admin
from .models import Stack, TakenProduct


class TakenProductAdminPanel(admin.ModelAdmin):
    list_display = ('product',  'variation', 'stack', 'quantity', 'is_available', )
    list_filter = ('is_available', 'variation', 'stack', 'quantity', )
    search_fields = ('product__name', 'product__name_fa', 'variation__color', 'variation__size', 
                     'stack__sid', 'stack__belongs_to__fname', 'stack__belongs_to__lname',)
    list_editable = ('is_available', )

class TakenProductInline(admin.TabularInline):
    model = TakenProduct
    extra = 0


class StackAdminPanel(admin.ModelAdmin):
    list_display = ('sid', 'belongs_to', 'cost', 'created')
    readonly_fields = ('sid', 'created')
    search_fields = ('sid', 'belongs_to__fname', 'belongs_to__lname', 'cost')
    inlines = (TakenProductInline, )


admin.site.register(Stack, StackAdminPanel)
admin.site.register(TakenProduct, TakenProductAdminPanel)
