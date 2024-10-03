from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Country_Codes, Category, Subcategory, Service_Type, \
    Collar, ServiceProvider, Dealer, Franchisee, Franchise_Type, \
    ServiceRegister, ServiceRequest, Customer, ServiceProvider
# Register your models here.

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'is_staff', 'is_superuser')
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(User, UserAdmin)
admin.site.register(Country_Codes)

admin.site.register(Category)
admin.site.register(Collar)
admin.site.register(Customer)
admin.site.register(Dealer)
admin.site.register(Franchisee)
admin.site.register(Franchise_Type)
admin.site.register(Service_Type)
admin.site.register(ServiceProvider)
admin.site.register(ServiceRegister)
admin.site.register(ServiceRequest)
admin.site.register(Subcategory)
