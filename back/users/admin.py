from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('phone_number', 'first_name', 'last_name', 'is_hr', 'is_active', 'is_staff')
    list_filter = ('is_hr', 'is_active', 'is_staff')
    list_editable = ('is_hr', 'is_active')
    search_fields = ('phone_number', 'first_name', 'last_name')
    ordering = ('phone_number',)

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Roles & permissions', {'fields': ('is_hr', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'first_name', 'last_name', 'is_hr'),
        }),
    )
