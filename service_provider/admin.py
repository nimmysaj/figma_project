from django.contrib import admin

# Register your models here.
from Accounts.models import ServiceProviderProfile, User
admin.site.register(ServiceProviderProfile)
admin.site.register(User)
