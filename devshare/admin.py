from django.contrib import admin
from .models import DevShare
# Register your models here.


class DevShareAdminPanel(admin.ModelAdmin):
    list_display = ('order', 'amount', 'status',)
    list_filter = ('order', 'amount', 'status', )

    readonly_fields = ('status', 'order', 'amount', )
    search_fields = ('order', 'status', 'amount')
    # inlines = (TakenProductInline, )


admin.site.register(DevShare, DevShareAdminPanel)