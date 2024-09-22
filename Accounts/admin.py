from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email','first_name', 'last_name','is_staff', 'is_customer', 'is_service_provider', 'phone_number')

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields' : ('is_customer', 'is_service_provider', 'phone_number')}),
    )

admin.site.register(User, CustomUserAdmin)

