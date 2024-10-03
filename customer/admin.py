from django.contrib import admin
from Accounts.models import ServiceProvider,ServiceRegister,Franchisee,Dealer

# Register your models here.
admin.site.register(ServiceRegister),
admin.site.register(ServiceProvider),
admin.site.register(Franchisee),
admin.site.register(Dealer)