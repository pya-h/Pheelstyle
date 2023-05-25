from django.contrib import admin
from .models import Shop, Gallery


class GalleryInlinePanel(admin.TabularInline):
    model = Gallery
    extra = 1

class ShopAdminPanel(admin.ModelAdmin):
    list_display = ('name_fa', 'owner')
    list_filter = ('owner', )
    search_fields = ('name', 'name_fa', 'owner', 'location')
    inlines = (GalleryInlinePanel, )


# Register your models here.
admin.site.register(Shop, ShopAdminPanel)
admin.site.register(Gallery)