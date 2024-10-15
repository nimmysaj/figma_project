from rest_framework import serializers
from Accounts.models import Country_Codes
from Accounts.models import User
import re


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # exclude = ['password']
        # fields = ['id','last_login','is_customer','is_service_provider','is_franchisee','is_dealer','is_active','email','full_name','nationality','designation','phone_number','is_active','is_staff']
        fields = '__all__'
        
    def validate_full_name(self, value):
        if not value:
            raise serializers.ValidationError("Full name is required.")
        return value

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    def validate_watsapp(self, value):
        if value and (len(value) != 10 or not value.isdigit()):
            raise serializers.ValidationError("WhatsApp number must be 10 digits long and numeric.")
        return value

    def validate_pin_code(self, value):
        if not value:
            raise serializers.ValidationError("PIN code is required.")
        if len(value) != 6 or not value.isdigit():
            raise serializers.ValidationError("PIN code must be 6 digits long and numeric.")
        return value
    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        # The regex requires the phone number to start with a + and be followed by 9 to 15 digits.
        regex = r'^\+\d{9,15}$'
        if not re.match(regex, value):
            raise serializers.ValidationError("Enter a valid phone number with country code (e.g., +1234567890).")
        return value

