from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Country_Codes

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_service_provider')}),  
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'phone_number', 'is_service_provider'),  
        }),
    )
    list_display = ('email', 'is_staff', 'is_superuser', 'is_service_provider', 'full_name', 'phone_number')  
    ordering = ('email',)

admin.site.register(User, UserAdmin)
admin.site.register(Country_Codes)
