from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from Accounts.models import User,Country_Codes
from .models import User,Customer,ServiceProvider,Franchisee,Franchise_Type,Dealer,OTP,District,State,ServiceRequest,Service_Type,ServiceRegister,Category,Subcategory,Collar, Invoice, CustomerReview

# Register your models here.

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'is_staff', 'is_superuser')
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(User)
admin.site.register(Country_Codes)
admin.site.register(Customer)
admin.site.register(ServiceProvider)
admin.site.register(Franchisee)
admin.site.register(Franchise_Type)
admin.site.register(Dealer)
admin.site.register(OTP)
admin.site.register(District)
admin.site.register(State)
admin.site.register(ServiceRequest)
admin.site.register(Service_Type)
admin.site.register(ServiceRegister)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Collar)
admin.site.register(Invoice)
admin.site.register(CustomerReview)