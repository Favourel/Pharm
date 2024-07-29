from django.contrib import admin
from .models import User, Notification, Prescription
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group


# Register your models here.


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('email', 'phone_number', 'first_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'phone_number', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'phone_number', 'address', 'first_name'),
        }),
    )
    
    
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
# admin.site.register(Notification)
admin.site.register(Prescription)

admin.site.site_header = "MAMSPHARMACY Administration"
admin.site.site_title = "MAMSPHARMACY Admin Portal"
admin.site.index_title = "Welcome to Your MAMSPHARMACY Admin"
