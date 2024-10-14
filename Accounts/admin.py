from django.contrib import admin
from .models import OTP, Category, Collar, Customer, CustomerReview, Dealer, District, Franchise_Type, Franchisee, Invoice, Service_Type, ServiceProvider, ServiceRegister, ServiceRequest, State, Subcategory, User, Country_Codes

admin.site.register(User)
admin.site.register(Customer)
admin.site.register(ServiceProvider)
admin.site.register(Franchisee)
admin.site.register(Franchise_Type)
admin.site.register(Dealer)
<<<<<<< HEAD
admin.site.register(OTP)
admin.site.register(District)
admin.site.register(State)
admin.site.register(CurrentLocation)
=======
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
>>>>>>> 6b1fe2019943d7f52171a342930b23a0f63528d3
