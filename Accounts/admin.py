from django.contrib import admin

from Accounts.models import OTP, ServiceProviderProfile

# Register your models here.
admin.site.register(ServiceProviderProfile)
admin.site.register(OTP)