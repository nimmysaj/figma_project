from rest_framework import serializers
from Accounts.models import *
import re
from datetime import datetime
from admin_app.models import *

class Franchise_Type_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Franchise_Type  # Specify the model to be serialized
        fields = ['id', 'name', 'details', 'amount', 'currency']

     # Field-level validation for 'name'
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("The name must be at least 3 characters long.")
        if len(value) > 50:
            raise serializers.ValidationError("The name must not exceed 50 characters.")
        if re.search(r'\d', value):
            raise serializers.ValidationError("The name must not contain numbers.")
        return value

     # Field-level validation for 'amount'
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("The amount must be greater than 0.")
        if value > 1000000:
            raise serializers.ValidationError("The amount must not exceed 1,000,000.")
        return value

    # Field-level validation for 'currency'
    def validate_currency(self, value):
        allowed_currencies = ['USD', 'EUR', 'INR', 'GBP', 'AUD', 'CAD', 'JPY', 'CNY', 'CHF', 'SGD']
        if value not in allowed_currencies:
            raise serializers.ValidationError(f"Currency must be one of {allowed_currencies}.")
        return value

class ServiceHistorySerializer(serializers.ModelSerializer):
    
    franchise = serializers.CharField(source='service.service_provider.franchisee.user.full_name', read_only=True)  # Assuming Franchisee model has 'name'
    fr_id = serializers.CharField(source='service.service_provider.franchisee.custom_id', read_only=True)  # Assuming Franchisee model has 'name'
    dealer = serializers.CharField(source='service.service_provider.dealer.user.full_name', read_only=True)  # Assuming Dealer model has 'name'
    d_id = serializers.CharField(source='service.service_provider.dealer.custom_id', read_only=True)  # Assuming Dealer model has 'name'
    service_provider_id = serializers.SerializerMethodField()
    cust_or_serv_id = serializers.SerializerMethodField() # Custom field for customer id whether it is customer or sp
    customer_type = serializers.SerializerMethodField()  # Custom field for customer type
    job_type = serializers.CharField(source='service.subcategory.service_type.name',read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'booking_id', 'request_date', 'franchise', 'fr_id', 'dealer', 'd_id',
            'service_provider_id', 'cust_or_serv_id', 'customer_type', 'job_type', 'work_status',
            'acceptance_status'
        ]


    def get_cust_or_serv_id(self, obj):
        # Attempt to fetch the custom_id from the SP model if SP(ie,customer is a SP : id exists in both models), or Customer model alone.
        custom_id1 = Customer.objects.filter(user_id=obj.customer.id).values_list('custom_id', flat=True).first()
        custom_id2 = ServiceProvider.objects.filter(user_id=obj.customer.id).values_list('custom_id', flat=True).first()
        
        if custom_id1 and custom_id2:
            return custom_id2  # Example: 'SP5D1FR1'
        elif not custom_id2:
            return custom_id1  # Example: 'USER1'
        else:
            return None #None if not found

    def get_service_provider_id(self, obj):
        # Get the id directly from the queryset
        service_provider_id = ServiceProvider.objects.filter(user_id=obj.service_provider.id).values_list('custom_id', flat=True).first()
        return service_provider_id  # This will return a string like 'SP5D1FR1'

    def get_customer_type(self, obj):
        # Determine if the user is a customer or service provider based on the ID prefix
        cust_id = self.get_cust_or_serv_id(obj)  # Fetch the custom ID

        if cust_id and cust_id.startswith('S'):
            return 'Service Provider'
        else:
            return 'Customer'
        return None

class FranchiseeDetailsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.full_name', read_only=True)  # Assuming Franchisee model has 'name'
    address = serializers.CharField(source='user.address', read_only=True)  # Assuming Franchisee model has 'address'
    contact = serializers.CharField(source='user.phone_number', read_only=True)  # Assuming Franchisee model has 'contact'
    email = serializers.CharField(source='user.email', read_only=True)  # Assuming Franchisee model has 'email'
    watsapp = serializers.SerializerMethodField()  # Custom field to include country code prefix

    class Meta:
        model = Franchisee
        fields = [
            'name', 'custom_id', 'profile_image', 'about', 'address', 'contact', 'email', 'watsapp'
        ]

    def get_watsapp(self, obj):
        # Check if both country code and watsapp are present
        country_code = obj.user.country_code.calling_code if obj.user.country_code else ''
        watsapp = obj.user.watsapp if obj.user.watsapp else ''
        
        # Return the formatted phone number with country code prefix
        if country_code and watsapp:
            return f"{country_code} {watsapp}"
        elif watsapp:
            return watsapp
        else:
            return None

# class NewAddSerializer(serializers.ModelSerializer):
#     ad_category_name = serializers.CharField(source='ad_category.ad_type', read_only=True) 
#     total_days = serializers.SerializerMethodField()
#     ad_user_name = serializers.CharField(source='ad_user.full_name', read_only=True)
#     total_amount = serializers.SerializerMethodField()

#     class Meta:
#         model = Ad_Management
#         fields = [
#             'title', 'description', 'ad_category_name', 'valid_from', 'valid_up_to', 'target_area', 'total_days', 'total_amount',
#             'image', 'ad_user_name'
#         ]

#    # Method to calculate total days
#     def get_total_days(self, obj):
#         if obj.valid_from and obj.valid_up_to:
#             delta = obj.valid_up_to - obj.valid_from  # Calculate date difference
#             return delta.days  # Return the number of days
#         return 0  # Return 0 if any date is missing

#     # Method to calculate total amount
#     def get_total_amount(self, obj):
#         total_days = self.get_total_days(obj)  # Get total days
#         if total_days and obj.ad_category.rate:
#             return total_days * obj.ad_category.rate  # Calculate total amount
#         return 0  # Return 0 if any value is missing

#     # Image validator to check dimensions
#     def validate_image(self, value):
#         image_file = Image.open(value)  # Open the uploaded image
        
#         # Get the ad category from the validated data
#         ad_category_id = self.initial_data.get('ad_category')
#         if not ad_category_id:
#             raise serializers.ValidationError("Ad category is required.")

#         # Retrieve expected dimensions from the Ad_category model
#         try:
#             ad_category_obj = Ad_category.objects.get(id=ad_category_id)
#         except Ad_category.DoesNotExist:
#             raise serializers.ValidationError("Invalid ad category.")

#         expected_width = ad_category_obj.image_width
#         expected_height = ad_category_obj.image_height

#         # Check if the uploaded image matches the expected dimensions
#         if image_file.width != expected_width or image_file.height != expected_height:
#             raise serializers.ValidationError(
#                 f"Image dimensions should be {expected_width}x{expected_height}px."
#             )
#         return value