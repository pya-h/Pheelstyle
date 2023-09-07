from django.contrib import admin
from .models import Product, Variation, Review, Gallery
import admin_thumbnails


@admin_thumbnails.thumbnail('image')
class GalleryInlinePanel(admin.TabularInline):
    model = Gallery
    extra = 1


class ProductAdminPanel(admin.ModelAdmin):
    list_display = ('name', 'category', 'modified', 'available',)
    list_editable = ('available', )
    prepopulated_fields = {'slug': ('name', )}
    list_filter = ('category', 'available', 'shop', 'discount', )
    search_fields = ('name', 'name_fa', 'category', 'shop__name', 'shop__name_fa', 'price', 'created',)
    inlines = (GalleryInlinePanel, )


class VariationAdminPanel(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'stock', 'is_available',)
    list_editable = ('is_available', 'stock',)
    list_editable = ('is_available', 'stock')
    list_filter = ('is_available', 'size', 'color', 'stock', )
    search_fields = ('size', 'color', 'product__name', 'product__name_fa')


admin.site.register(Product, ProductAdminPanel)
admin.site.register(Variation, VariationAdminPanel)
admin.site.register(Review)
admin.site.register(Gallery)

