from django.contrib import admin

from Accounts.models import Country_Codes, Customer, District, State, User,ServiceRequest,ServiceRegister,ServiceProvider,Dealer,Franchisee,Franchise_Type,Category,Subcategory,Service_Type,Collar


admin.site.register(District)
admin.site.register(Country_Codes)
admin.site.register(State)
admin.site.register(User)
admin.site.register(Customer)
admin.site.register(ServiceRequest)
admin.site.register(ServiceRegister)
admin.site.register(ServiceProvider)
admin.site.register(Dealer)
admin.site.register(Franchisee)
admin.site.register(Franchise_Type)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Service_Type)
admin.site.register(Collar)