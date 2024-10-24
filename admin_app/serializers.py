from rest_framework import serializers
from Accounts.models import User, Franchisee ,Payment ,Customer ,Dealer  ,Service_Type ,Collar
from django.db import models 
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
# User Serializer
class UserSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone_number', 'password','landmark','address','district','state','watsapp','country_code','pin_code']

    # Validate email field
    def validate_email(self, value):
        try:
            validate_email(value)  # Django's built-in email validator
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        
        return value

    # Validate phone number field
    def validate_phone_number(self, value):
        # Example regex for phone numbers (adjust based on your country format)
        phone_regex = re.compile(r'^\+?\d{10,15}$')  # Accepts phone numbers between 10 and 15 digits
        
        if not phone_regex.match(value):
            raise serializers.ValidationError("Enter a valid phone number (10-15 digits).")
        
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        
        return value


    def create(self, validated_data):
        user = User(
            email=validated_data.get('email'),
            full_name=validated_data.get('full_name'),
            phone_number=validated_data.get('phone_number'),
            landmark=validated_data.get('landmark'),
            address=validated_data.get('address'),
            district=validated_data.get('district'),
            state=validated_data.get('state'),
            watsapp=validated_data.get('watsapp'),
            country_code=validated_data.get('country_code'),
            pin_code=validated_data.get('pin_code'),
            )
        
        user.set_password(validated_data.get('password'))  
        user.save()
        return user


class FranchiseeSerializer(serializers.ModelSerializer):
    
    district_name = serializers.SerializerMethodField()
    user = UserSerializer() 

    class Meta:
        model = Franchisee
        fields = ['about', 'revenue', 'dealers', 'service_providers', 'type', 'valid_from', 
                  'valid_up_to', 'status', 'verification_id', 'verificationid_number', 'community_name','profile_image' ,'user','district_name']
        
    def get_district_name(self, obj):
        # Access the district name via the related user object
        return obj.user.district.name if obj.user.district else None

    def create(self, validated_data):
        user_data = validated_data.pop('user')  
        user = UserSerializer.create(UserSerializer(), validated_data=user_data,) 
        user.is_franchisee = True
        user.save()
        franchisee = Franchisee.objects.create(user=user,**validated_data) 
        return franchisee

    def update(self, instance, validated_data):

        user_data = validated_data.pop('user', None)
        instance.about = validated_data.get('about', instance.about)
        instance.revenue = validated_data.get('revenue', instance.revenue)
        instance.dealers = validated_data.get('dealers', instance.dealers)
        instance.service_providers = validated_data.get('service_providers', instance.service_providers)
        instance.type = validated_data.get('type', instance.type)
        instance.valid_from = validated_data.get('valid_from', instance.valid_from)
        instance.valid_up_to = validated_data.get('valid_up_to', instance.valid_up_to)
        instance.status = validated_data.get('status', instance.status)
        instance.verification_id = validated_data.get('verification_id', instance.verification_id)
        instance.verificationid_number = validated_data.get('verificationid_number', instance.verificationid_number)
        instance.community_name = validated_data.get('community_name', instance.community_name)
        
        profile_image = validated_data.get('profile_image')
        if profile_image:
            instance.profile_image = profile_image
        
        instance.save()

        if user_data:
            user = instance.user
            user.email = user_data.get('email', user.email)
            user.full_name = user_data.get('full_name', user.full_name)
            user.phone_number = user_data.get('phone_number', user.phone_number)
            user.landmark = user_data.get('landmark', user.landmark)
            user.address = user_data.get('address', user.address)
            user.district = user_data.get('district', user.district)
            user.state = user_data.get('state', user.state)
            user.watsapp = user_data.get('watsapp', user.watsapp)
            user.country_code = user_data.get('country_code', user.country_code)
            user.pin_code = user_data.get('pin_code', user.pin_code)

            if user_data.get('password'):
                user.set_password(user_data['password'])

            user.save()

        return instance



class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['transaction_id', 'invoice', 'description', 'amount_paid',
                  'payment_method', 'payment_date', 'payment_status', 'sender', 'receiver']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Safely get the invoice type
        representation['type'] = getattr(instance.invoice, 'invoice_type', None)

        # Initialize sender to None
        sender = None
        if instance.sender.is_customer:
            try:
                # Fetch the Customer data using sender's user_id
                customerdata = Customer.objects.get(user_id=instance.sender.id)
                sender = customerdata.custom_id
            except Customer.DoesNotExist:
                sender = None  # If the customer does not exist, handle it gracefully

        elif instance.sender.is_franchisee:
            try:
                # Fetch the Franchisee data using sender's user_id
                franchiseedata = Franchisee.objects.get(user_id=instance.sender.id)
                sender = franchiseedata.custom_id
            except Franchisee.DoesNotExist:
                sender = None  # If the franchisee does not exist, handle it gracefully

        elif instance.sender.is_dealer:
            try:
                # Fetch the Dealer data using sender's user_id
                dealerdata = Dealer.objects.get(user_id=instance.sender.id)
                sender = dealerdata.custom_id
            except Dealer.DoesNotExist:
                sender = None  # If the dealer does not exist, handle it gracefully

        # Set the sender and receiver fields
        representation['sender'] = sender
        representation['receiver'] = instance.receiver.id

        return representation


    
# class TransactionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Payment
#         fields = ['transaction_id', 'invoice', 'description', 'amount_paid',
#                   'payment_method', 'payment_date', 'payment_status','sender','receiver']

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)

#         # Safely get the invoice type
#         representation['type'] = getattr(instance.invoice, 'invoice_type', None)

#         # Initialize sender to None
#         sender = None
#         if instance.sender.is_customer:
#             try:
#                 # Fetch the Customer data using sender's user_id
#                 customerdata = Customer.objects.get(user_id=instance.sender.id)
#                 sender = customerdata.custom_id
#             except Customer.DoesNotExist:
#                 sender = None  # If the customer does not exist, handle it gracefully
                
#         elif instance.sender.is_franchisee:
#             try:
#                 # Fetch the Franchisee data using sender's user_id
#                 franchiseedata = Franchisee.objects.get(user_id=instance.sender.id)
#                 sender = franchiseedata.custom_id
#             except Franchisee.DoesNotExist:
#                 sender = None  # If the franchisee does not exist, handle it gracefully
#         elif instance.sender.is_dealer:
#             try:
#                 # Fetch the Dealer data using sender's user_id
#                 dealerdata = Dealer.objects.get(user_id=instance.sender.id)
#                 sender = dealerdata.custom_id
#             except Dealer.DoesNotExist:
#                 sender = None  # If the dealer does not exist, handle it gracefully
                
#         representation['receiver'] = instance.receiver.id
#         representation['sender'] = sender

#         return representation


# TASK 3 SERVICE TYPE CRUD //////////////////////////////////////////////////////////////////////////////////////////////////

class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service_Type
        fields = ['id', 'name', 'details', 'currency']
        
    def validate_name(self, value):
        """Ensure name uniqueness, except for the current instance."""
        service_id = self.instance.id if self.instance else None

        if Service_Type.objects.filter(name=value).exclude(id=service_id).exists():
            raise serializers.ValidationError("A service type with this name already exists.")
        
        return value
    
# TASK 3 Collor CRUD //////////////////////////////////////////////////////////////////////////////////////////////////

class CollarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collar
        fields = ['id', 'name', 'lead_quantity', 'amount']

    def validate_name(self, value):
        """Check for duplicate collar names."""
        # Allow the current instance's name to pass the validation during updates
        if self.instance and self.instance.name == value:
            return value
        if Collar.objects.filter(name=value).exists():
            raise serializers.ValidationError("A collar with this name already exists.")
        return value

    def update(self, instance, validated_data):
        """Update the Collar object."""
        instance.name = validated_data.get('name', instance.name)
        instance.lead_quantity = validated_data.get('lead_quantity', instance.lead_quantity)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance