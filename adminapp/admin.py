from django.contrib import admin

# Register your models here.
from .models import ServiceRequest
from .models import ServiceRegister
from .models import Collar
from .models import Category
from .models import Subcategory
from .models import Service_Type

admin.site.register(ServiceRequest)
admin.site.register(ServiceRegister)
admin.site.register(Collar)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Service_Type)