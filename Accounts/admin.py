from django.contrib import admin
from .models import Invoice, Payment
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User

# Customize the default UserAdmin
class UserAdmin(DefaultUserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('id',)


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'invoice_type', 'sender', 'receiver', 'total_amount', 'payment_status', 'invoice_date', 'due_date')
    search_fields = ('invoice_number', 'sender__username', 'receiver__username', 'invoice_type')
    list_filter = ('payment_status', 'invoice_type', 'invoice_date')
    ordering = ('-invoice_date',)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'sender', 'receiver', 'amount_paid', 'payment_method', 'payment_status', 'payment_date')
    search_fields = ('invoice__invoice_number', 'sender__username', 'receiver__username', 'payment_method')
    list_filter = ('payment_status', 'payment_method', 'payment_date')
    ordering = ('-payment_date',)

# Register your models here.
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Payment, PaymentAdmin)
# Unregister the default User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

