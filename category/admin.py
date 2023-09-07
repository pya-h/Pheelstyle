from django.contrib import admin
from .models import Category


class CategoryAdminPanel(admin.ModelAdmin):
    list_display = ['name_fa', 'slug']
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ('name', 'name_fa', )


admin.site.register(Category, CategoryAdminPanel)
