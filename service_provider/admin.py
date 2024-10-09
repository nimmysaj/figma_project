from django.contrib import admin
from Accounts.models import User,Dealer,Franchisee,Franchise_Type,ServiceProvider, District, State, Complaint, ServiceRequest, ServiceRegister,Category,Subcategory,Service_Type,Collar

# Register your models here.
# admin.site.register(User)
admin.site.register(Dealer)
admin.site.register(Franchisee)
admin.site.register(Franchise_Type)
admin.site.register(ServiceProvider)
admin.site.register(District)
admin.site.register(State)
admin.site.register(Complaint)
admin.site.register(ServiceRequest)
admin.site.register(ServiceRegister)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Service_Type)
admin.site.register(Collar)
