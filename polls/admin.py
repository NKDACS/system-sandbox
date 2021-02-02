from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# def delete(modeladmin, request, queryset):


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('first_name', 'last_name',
                             'email', 'number', 'phone', 'person_id')}),
        ('权限', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')


admin.site.register(MyUser, MyUserAdmin)

admin.site.register([Resume, Anoucement])
