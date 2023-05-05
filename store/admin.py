from django.contrib import admin
from .models import Product, Variation, Review, Gallery
import admin_thumbnails


@admin_thumbnails.thumbnail('image')
class GalleryInlinePanel(admin.TabularInline):
    model = Gallery
    extra = 1


class ProductAdminPanel(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'modified', 'available',)
    prepopulated_fields = {'slug': ('name', )}
    list_filter = ('category', 'price', 'discount', )
    search_fields = ('name', 'name_fa', )
    inlines = (GalleryInlinePanel, )


class VariationAdminPanel(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'is_available', 'stock')
    list_editable = ('is_available', )
    list_filter = ('product', 'size', 'color', 'is_available', 'stock', )
    search_fields = ('size', 'color', 'product')


admin.site.register(Product, ProductAdminPanel)
admin.site.register(Variation, VariationAdminPanel)
admin.site.register(Review)
admin.site.register(Gallery)

