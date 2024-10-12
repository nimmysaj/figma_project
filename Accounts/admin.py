from django.contrib import admin

from Accounts.models import Country_Codes, Customer, District, State, User


admin.site.register(District)
admin.site.register(Country_Codes)
admin.site.register(State)
admin.site.register(User)
admin.site.register(Customer)