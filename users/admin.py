from django.contrib import admin
from .models import User, Notification, Prescription
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group


# Register your models here.


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('email', 'phone_number')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('phone_number', 'picture_url', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'phone_number', 'picture_url', 'address'),
        }),
    )
    
    
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Notification)
admin.site.register(Prescription)
