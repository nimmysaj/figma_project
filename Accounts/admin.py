from django.contrib import admin
from .models import Invoice, Payment, User

# Register your models here.
admin.site.register(Invoice)
admin.site.register(Payment)
admin.site.register(User)


