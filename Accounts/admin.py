from django.contrib import admin
from .models import OTP, Category, Collar, Customer, CustomerReview, Dealer, District, Franchise_Type, Franchisee, Invoice, Service_Type, ServiceProvider, ServiceRegister, ServiceRequest, State, Subcategory, User, Country_Codes

admin.site.register(User)
admin.site.register(Customer)
@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('id','custom_id', 'user', 'dealer', 'franchisee', 'payout_required', 'status', 'verification_by_dealer')

    # Fields to allow searching
    search_fields = ('custom_id', 'user__username', 'dealer__custom_id', 'franchisee__custom_id', 'status')

    # Default ordering (by 'user' and 'custom_id')
    ordering = ('user', 'custom_id')

    # Optionally, you can make `list_filter` for easy filtering
    list_filter = ('status', 'payout_required', 'verification_by_dealer')
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
admin.site.register(CustomerReview)
