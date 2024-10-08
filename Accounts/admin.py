from django.contrib import admin
from .models import Complaint, ServiceRequest, Invoice
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Category, Collar, Dealer, Franchise_Type, Franchisee, Service_Type, ServiceProvider, ServiceRegister, Subcategory, User,Country_Codes
# Register your models here.

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'is_staff', 'is_superuser')
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(User, UserAdmin)
admin.site.register(Country_Codes)


class ServiceRegisterAdmin(admin.ModelAdmin):
    list_display = ('id',  'service_provider',  'description', 'gstcode', 'status',
                    'category', 'subcategory', 'license', 'image', 'accepted_terms','available_lead_balance')

# Register the model with the custom admin class
admin.site.register(ServiceRegister, ServiceRegisterAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status')

# Register the model with the custom admin class
admin.site.register(Category, CategoryAdmin)

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title','collar', 'category','service_type','status')

# Register the model with the custom admin class
admin.site.register(Subcategory, SubCategoryAdmin)


@admin.register(Franchisee)
class FranchiseeAdmin(admin.ModelAdmin):
    list_display = ('custom_id', 'user', 'type', 'community_name', 'revenue', 'dealers', 'service_providers', 'status', 'valid_from', 'valid_up_to')  # Columns to display
    list_filter = ('status', 'type', 'valid_from', 'valid_up_to')  # Filters for the sidebar
    search_fields = ('custom_id', 'user__username', 'community_name')  # Fields to search by
    ordering = ('valid_from',)  # Default ordering by 'valid_from' field

@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ('custom_id', 'user', 'franchisee', 'service_providers', 'status', 'verification_id')  # Columns to display
    list_filter = ('status', 'franchisee')  # Filters for the sidebar
    search_fields = ('custom_id', 'user__username', 'franchisee__custom_id')  # Fields to search by
    ordering = ('user',)  # Default ordering by 'user'

@admin.register(Franchise_Type)
class FranchiseTypeAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('name', 'amount', 'currency')

    # Fields to allow searching
    search_fields = ('name', 'details', 'currency')

    # Default ordering (by 'name' and 'amount')
    ordering = ('name', 'amount')

    # Optionally, you can make `list_filter` for easy filtering
    list_filter = ('currency',)


class CollarAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'lead_quantity','amount')

# Register the model with the custom admin class
admin.site.register(Collar, CollarAdmin)

class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','details')

# Register the model with the custom admin class
admin.site.register(Service_Type, ServiceTypeAdmin)

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('id','custom_id', 'user', 'dealer', 'franchisee', 'payout_required', 'status', 'verification_by_dealer')

    # Fields to allow searching
    search_fields = ('custom_id', 'user__username', 'dealer__custom_id', 'franchisee__custom_id', 'status')

    # Default ordering (by 'user' and 'custom_id')
    ordering = ('user', 'custom_id')

    # Optionally, you can make `list_filter` for easy filtering
    list_filter = ('status', 'payout_required', 'verification_by_dealer')




@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service_provider', 'service', 'work_status', 'acceptance_status', 'request_date', 'availability_from', 'availability_to')
    search_fields = ('customer__full_name', 'service_provider__full_name', 'service__title')
    list_filter = ('work_status', 'acceptance_status', 'request_date')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'invoice_type', 'service_request', 'sender', 'receiver', 'price', 'total_amount', 'payment_status', 'invoice_date', 'due_date')
    search_fields = ('invoice_number', 'sender__full_name', 'receiver__full_name')
    list_filter = ('invoice_type', 'payment_status', 'invoice_date')

class ComplaintAdmin(admin.ModelAdmin):
    # Fields to be displayed in the admin list view
    list_display = ('id', 'customer', 'service_provider', 'subject', 'status', 'submitted_at', 'resolved_at')
    
    # Fields to be searchable
    search_fields = ('subject', 'customer__username', 'service_provider__username', 'description')
    
    # Filters for the admin list view
    list_filter = ('status', 'submitted_at', 'resolved_at', 'service_provider')

    # Optional: Making 'subject' and 'status' editable in the list view
    list_editable = ('status',)

    # Ordering the list by submission date
    ordering = ('-submitted_at',)

# Registering the Complaint model with the custom admin class
admin.site.register(Complaint, ComplaintAdmin)