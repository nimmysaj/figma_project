from rest_framework import serializers
from Accounts.models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from Accounts.models import phone_regex
from django.core.exceptions import ValidationError as DjangoValidationError


# serializers.py


# TASK 1 Franchisee Registration ////////////////////////////////////////////////////////////////////////////////////

class UserSerializer(serializers.ModelSerializer):
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), required=True)
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all(), required=True)
    country_code = serializers.PrimaryKeyRelatedField(queryset=Country_Codes.objects.all(), required=True)

    class Meta:
        model = User
        fields = [
            'email', 'phone_number', 'full_name', 'landmark', 'address', 
            'district', 'state', 'watsapp', 'country_code', 'pin_code', 'password'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        # Skip uniqueness check if updating with the same email
        if self.instance and self.instance.email == value:
            return value
        # Otherwise, check if email exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_phone_number(self, value):
        # Skip uniqueness check if updating with the same phone number
        if self.instance and self.instance.phone_number == value:
            return value
        # Otherwise, check if phone number exists
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("User with this phone number already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
class FranchiseeSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested serializer for user data
    district_name = serializers.SerializerMethodField()
    Amount_to_pay = serializers.SerializerMethodField()
    class Meta:
        model = Franchisee
        fields = [
            'id','custom_id',
            'user', 
            'about', 'profile_image', 'revenue', 'dealers', 
            'service_providers', 'type', 'valid_from', 'valid_up_to', 
            'verification_id', 'verificationid_number', 'community_name','district_name','Amount_to_pay','status',
        ]

    def get_district_name(self, obj):
        return obj.user.district.name if obj.user.district else None

    def get_Amount_to_pay(self, obj):
        return obj.type.amount if obj.type else None

    def create(self, validated_data):
        user_data = validated_data.pop('user')

        # Ensure email and phone_number are required for creation
        if 'email' not in user_data or 'phone_number' not in user_data:
            raise serializers.ValidationError("Both email and phone number are required to create a new franchisee.")
        
        user_data['is_franchisee'] = True

        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        franchisee = Franchisee.objects.create(user=user, **validated_data)
        
        return franchisee

    def update(self, instance, validated_data):
        # Extract user data if provided
        user_data = validated_data.pop('user', None)

        # Update the user information if user_data is provided
        if user_data:
            for attr, value in user_data.items():
                if attr == 'password' and value:  # Check if password is being updated
                    instance.user.set_password(value)  # Hash the new password
                else:
                    setattr(instance.user, attr, value)
            instance.user.save()  # Save changes to the user

        # Update the remaining franchisee fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()  # Save changes to the franchisee

        return instance
    
    
    
    
# TASK 2 Transaction History ////////////////////////////////////////////////////////////////////////////////////
 
    
    
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
    
    
    
    
# TASK 4 Ad category //////////////////////////////////////////////////////////////////////////////////////////////////

class AdCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad_category
        fields = '__all__'
    def validate_type(self, value):
        """Ensure that the same ad type cannot be posted more than once."""
        if self.instance:  # If this is an update
            # If the 'type' is unchanged, allow it
            if self.instance.type == value:
                return value
        
        # For both new and changed types, check for duplicates
        if Ad_category.objects.filter(type=value).exists():
            raise serializers.ValidationError(f"An Ad Category with type '{value}' already exists.")

        return value