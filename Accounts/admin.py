#from django.contrib import admin
from django.contrib import admin
from Accounts.models import User
from django.contrib.auth.models import User
#from django.contrib import admin
#from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User,Country_Codes
from .models import OTP, Category, Collar, Customer, CustomerReview, Dealer, Ad_Management, Ad_category, District, Franchise_Type,Franchisee, Invoice, Service_Type, ServiceProvider, ServiceRegister, ServiceRequest, State, Subcategory, User, Country_Codes,Payment


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'nationality', 'designation', 'is_staff', 'is_active')
    search_fields = ('email', 'full_name', 'nationality', 'designation')
    fieldsets = (
        (None, {
            'fields': ('email', 'full_name', 'nationality', 'designation', 'password')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Roles', {
            'fields': ('is_customer', 'is_service_provider', 'is_franchisee', 'is_dealer'),
        }),
    )


admin.site.register(User)
admin.site.register(Customer)
admin.site.register(ServiceProvider)
admin.site.register(Franchisee)
admin.site.register(Franchise_Type)
admin.site.register(Dealer)
admin.site.register(Country_Codes)
admin.site.register(OTP)
admin.site.register(District)
admin.site.register(State)
admin.site.register(ServiceRegister)
admin.site.register(ServiceRequest)
admin.site.register(Collar)
admin.site.register(Service_Type)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Invoice)
admin.site.register(Payment)
admin.site.register(CustomerReview)
admin.site.register(Ad_Management)
admin.site.register(Ad_category)
