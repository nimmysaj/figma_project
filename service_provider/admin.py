from django.contrib import admin
from Accounts.models import User,Dealer,Franchisee,Franchise_Type,ServiceProvider

# Register your models here.
# admin.site.register(User)
admin.site.register(Dealer)
admin.site.register(Franchisee)
admin.site.register(Franchise_Type)
admin.site.register(ServiceProvider)