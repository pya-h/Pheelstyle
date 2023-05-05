from django.contrib import admin
from .models import User, Profile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html


class UserAdminPanel(UserAdmin):
    list_display = ('phone', 'fname', 'lname', 'email', 'joined', 'last_login', 'activated')
    list_display_links = ('phone', 'email')
    readonly_fields = ('id', 'joined', 'last_login')
    ordering = ('-joined', )  # sort list by date_joined descending order
    filter_horizontal = ()
    search_fields = ('phone', 'fname', 'lname', 'email', )
    list_filter = ('activated', 'is_superuser', 'is_admin', 'is_staff', )
    fieldsets = (('ناموس', {'fields': ('phone', 'password', 'id')}),
                 ('اصل', {'fields': ('fname', 'lname', 'email', 'joined')}),
                 ('دسترسی ها', {'fields': ('is_superuser', 'is_admin', 'is_staff', 'activated')}),)

    add_fieldsets = (('ناموس', {'fields': ('phone', 'password')}),
                     ('اصل', {'fields': ('fname', 'lname', 'email', 'joined')}),
                     ('دسترسی ها', {'fields': ('is_admin', 'is_staff')}),)


class ProfilePanel(admin.ModelAdmin):
    def avatar_thumbnail(self, obj):
        return format_html('<img src="{}" width="48" height="48" style="border-radius: 50%;" />'.format(obj.avatar.url if obj.avatar else "/static/images/noavatar.jpeg"))
    avatar_thumbnail.short_description = 'Avatar'
    list_display = ('avatar_thumbnail', 'user', 'province', 'city')


admin.site.register(User, UserAdminPanel)
admin.site.register(Profile, ProfilePanel)
