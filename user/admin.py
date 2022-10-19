from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin


class UserAdminPanel(UserAdmin):
    list_display = ('phone', 'fname', 'lname', 'email', 'joined', 'last_login', 'activated')
    list_display_links = ('phone', 'email')
    readonly_fields = ('id', 'joined', 'last_login')
    ordering = ('-joined', )  # sort list by date_joined descending order
    filter_horizontal = ()
    search_fields = ('phone', 'fname', 'lname', 'email', )
    list_filter = ('activated', 'is_superuser', 'is_admin', 'is_staff', )
    fieldsets = (('Credentials', {'fields': ('phone', 'password', 'id')}),
                 ('Personal Info', {'fields': ('fname', 'lname', 'email', 'joined')}),
                 ('Permissions', {'fields': ('is_superuser', 'is_admin', 'is_staff', 'activated')}),)

    add_fieldsets = (('Credentials', {'fields': ('phone', 'password')}),
                     ('Personal Info', {'fields': ('fname', 'lname', 'email', 'joined')}),
                     ('Permissions', {'fields': ('is_admin', 'is_staff')}),)


admin.site.register(User, UserAdminPanel)
