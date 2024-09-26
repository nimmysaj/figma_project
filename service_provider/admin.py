from django.contrib import admin

# Register your models here.
from Accounts.models import ServiceProvider, User, Franchisee, Dealer, Franchise_Type
admin.site.register(ServiceProvider)
admin.site.register(Franchisee)
admin.site.register(Dealer)
admin.site.register(Franchise_Type)
