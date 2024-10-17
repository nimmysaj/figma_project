import re
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from Accounts.models import Franchise_Type,ServiceProvider,ServiceRequest,Invoice,Customer,User,Franchisee

VALID_CURRENCY_CODES = ['USD', 'EUR', 'GBP', 'INR', 'JPY', 'CAD', 'AUD']
class FranchiseTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Franchise_Type
        fields=['id','name','details','amount','currency']
        
    def validate_name(self, value):
        if 'franchise' not in value.lower():
            raise serializers.ValidationError("Franchise name must include the word 'franchise'.")
        return value
    
    # Custom validation for currency field
    def validate_currency(self, value):
        value = value.upper()  # Make sure the currency is in uppercase
        if value not in VALID_CURRENCY_CODES:
            raise serializers.ValidationError(f"Invalid currency code: {value}. Supported currencies: {', '.join(VALID_CURRENCY_CODES)}")
        return value
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive number.")
        if value > 1000000:  # For example, limit the amount to 1,000,000
            raise serializers.ValidationError("Amount exceeds the maximum allowed value of 1,000,000.")
        return value


class customerTypeserializer(serializers.ModelSerializer):
    customer_id=serializers.SerializerMethodField()
    
    class Meta:
        model=User
        fields=['is_customer',
            'is_service_provider' ,
            'is_franchisee',
            'is_dealer' ]
    
    def get_customer_id(self,obj):
        
        if self.customer in Customer:  # Assuming `is_customer` is a Boolean field in Customer model
            return Customer.custom_id,'Is Customer'
        elif self.customer in ServiceProvider:
            return ServiceProvider.custom_id,
        
        else :return 'Unknown'
    

class ServiceHistorySerializer(serializers.ModelSerializer):
    franchisee = serializers.CharField(source='service.service_provider.franchisee.user', read_only=True)
    franchisee_id=serializers.CharField(source='service.service_provider.franchisee.custom_id')
    dealer = serializers.CharField(source='service.service_provider.dealer.user', read_only=True)
    customer = serializers.CharField(source='customer.name', read_only=True)  # Assuming customer has a 'name' field
    customertype = serializers.SerializerMethodField()
    #customer_id=serializers.CharField(source='customer')
    #invoice_date = serializers.SerializerMethodField()  # Assuming ServiceRequest has a 'service_date' field
    request_date=serializers.SerializerMethodField()
    service_provider_id= serializers.CharField(source='service.service_provider.custom_id',read_only=True)
    service_provider= serializers.CharField(source='service.service_provider.user',read_only=True)
    customer_custom_id=serializers.SerializerMethodField()
    job_type=serializers.CharField(source='service.subcategory.service_type.name',read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = [
            'booking_id',      # Request ID
            'request_date',
            'franchisee_id',
            'franchisee',  # Franchisee
            'dealer',      # Dealer
            'service_provider_id',
            'service_provider',
            'customer_custom_id',
            'customer',
            'customertype',
            # Customer type (from the get_customer_type method)
            'work_status', # Status (service request status)
            'job_type',
                     # Service request date

        ]

    # Method to determine the customer type
    def get_customer_custom_id(self, obj):
       customidc=Customer.objects.filter(user_id=obj.customer.id).values_list('custom_id',flat=True).first()
       customids=ServiceProvider.objects.filter(user_id=obj.customer.id).values_list('custom_id',flat=True).first()
       if customidc and customids:
           return customids
       elif not customids:
            
            return customidc
       else :
           return None

    def get_customertype(self, obj):
        cust_id=self.get_customer_custom_id(obj)
        if cust_id and cust_id.startswith('S'):
            return 'Service Provider'
        else:
            return 'Customer'
        return None
        
    def get_service_provider_id(self, obj):
        # Get the service provider's ID where status is 'accepted' or 'pending'
        return obj.service_provider if obj.work_status in ['In Progress', 'pending','Completed']else None

    from datetime import  datetime
    def get_request_date(self, obj):
        if obj.request_date:
            return obj.request_date.strftime("%B %d, %Y")  # Format as "Month Day, Year"
        return None
    #def get_invoice_date(self, obj):
    # Fetch the latest invoice associated with the service request (if any)
    #    invoice = obj.invoices.order_by('-invoice_date').first()  # Assuming 'invoices' is the related name for Invoice
    #    if invoice:
    #        return invoice.invoice_date.strftime('%B %d, %Y')  # Access the invoice_date field on the Invoice object
    #    return None  # If no invoice is found

class FranchiseeDetailsSerializer(serializers.ModelSerializer):
    full_name=serializers.CharField(source='user.full_name',read_only=True)
    email=serializers.EmailField(source='user.email',read_only=True)
    whatsapp=serializers.CharField(source='user.whatsapp',read_only=True)
    phone_number=serializers.CharField(source='user.phone_number',read_only=True)
    country_code=serializers.CharField(source='user.country_code',read_only=True)
    address=serializers.CharField(source='user.address',read_only=True)
    class Meta:
        model=Franchisee
        fields=['user','custom_id','full_name','about','profile_image','address','email','whatsapp','phone_number','country_code']