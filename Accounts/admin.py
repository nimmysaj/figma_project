from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from Accounts.models import *
from admin_app.models import *

admin.site.register(User)
admin.site.register(DeclineServiceModel)
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
admin.site.register(Complaint)
admin.site.register(Service_Type)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Invoice)
<<<<<<< HEAD
admin.site.register(Payment)
admin.site.register(CustomerReview)
=======
admin.site.register(CustomerReview)
#admin.site.register(Ad_category)
#admin.site.register(Ad_Management)
>>>>>>> 4f71b3d47b16763174a25b1294db4b1140007294
