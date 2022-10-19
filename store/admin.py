from django.contrib import admin
from .models import Product, Variation, Review


class ProductAdminPanel(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'modified', 'available',)
    prepopulated_fields = {'slug': ('name', )}
    list_filter = ('category', 'price', 'discount', )
    search_fields = ('name', 'name_fa', )


class VariationAdminPanel(admin.ModelAdmin):
    list_display = ('product', 'parameter', 'value', 'is_available', 'stock')
    list_editable = ('is_available', )
    list_filter = ('product', 'parameter', 'value', 'is_available', 'stock', )
    search_fields = ('parameter', 'value', )


admin.site.register(Product, ProductAdminPanel)
admin.site.register(Variation, VariationAdminPanel)
admin.site.register(Review)
