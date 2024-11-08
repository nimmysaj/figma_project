from django.contrib import admin
from .models import Franchise_Type,Franchisee,Service_Type,ServiceProvider,Dealer,User

admin.site.register(Franchise_Type),
admin.site.register(Franchisee),
admin.site.register(Service_Type),
admin.site.register(ServiceProvider),
admin.site.register(Dealer),
admin.site.register(User)