from rest_framework import serializers
from Accounts.models import User,Franchisee,Franchise_Type
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
import re  # For regex validation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']
        # fields = ['id','last_login','is_customer','is_service_provider','is_franchisee','is_dealer','is_active','email','full_name','nationality','designation','phone_number','is_active','is_staff']
        # fields = '__all__'
        # Custom validation for the full_name field

    def validate_full_name(self, value):
        if not value:
            raise serializers.ValidationError("Full name is required.")
        if len(value) < 3:
            raise serializers.ValidationError("Full name must be at least 3 characters long.")
        return value

        # Custom validation for the email field

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise serializers.ValidationError("Enter a valid email address.")
        return value

        # Custom validation for the password field

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Password is required.")
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

        # Custom validation for the whatsapp number field

    def validate_whatsapp(self, value):
        if not value:
            raise serializers.ValidationError("WhatsApp number is required.")
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Enter a valid WhatsApp number (10 digits).")
        return value

        # Custom validation for the pincode field

    def validate_pin_code(self, value):
        if not value:
            raise serializers.ValidationError("Pin code is required.")
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Enter a valid 6-digit pin code.")
        return value
        # Custom validation for the phone number field

    # def validate_phone_number(self, value):
    #     if not value:
    #         raise serializers.ValidationError("Phone number is required.")
    #     if not value.isdigit():
    #         raise serializers.ValidationError("Phone number must contain only digits.")
    #     if len(value) != 10:
    #         raise serializers.ValidationError("Phone number must be exactly 10 digits.")
    #     return value

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        # The regex requires the phone number to start with a `+` and be followed by 9 to 15 digits.
        regex = r'^\+\d{9,15}$'
        if not re.match(regex, value):
            raise serializers.ValidationError("Enter a valid phone number with country code (e.g., +1234567890).")
        return value



class FranchiseeSerializer(serializers.ModelSerializer):
    is_franchisee = serializers.CharField(source='user.is_franchisee')  # Fetching from User model
    location = serializers.CharField(source='user.address')  # Location (from User)
    contact = serializers.CharField(source='user.phone_number')  # Contact (from User)
    class Meta:
        model = Franchisee
        fields = [
            'is_franchisee',   # From User model
            'custom_id',        # From Franchisee model
            'revenue',          # From Franchisee model
            'dealers',          # Representing branches (from Franchisee)
            'service_providers', # From Franchisee model
            'location',         # From User model
            'contact',          # From User model
            'valid_up_to',      # From Franchisee model
            'status'            # From Franchisee model
        ]
class FranchiseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Franchise_Type
        fields = ['id', 'name', 'details', 'amount', 'currency']