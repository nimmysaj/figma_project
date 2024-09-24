from django.contrib import admin

from Accounts.models import ServiceType,Collar,Category,Subcategory,ServiceRegister,ServiceProviderProfile

# Register your models here.


admin.site.register(ServiceType)
admin.site.register(Collar)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(ServiceRegister)
admin.site.register(ServiceProviderProfile)


