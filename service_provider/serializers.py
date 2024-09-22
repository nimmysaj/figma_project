from rest_framework import serializers
from django.contrib.auth import get_user_model
from Accounts.models import OTP,User  # Make sure this points to your OTP model
import re

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)

    

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.match(r'^[A-Z]', value):
            raise serializers.ValidationError("Password must start with an uppercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[@$!%*?&]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email is already registered.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove confirm_password
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = False 
        user.is_service_provider=True
        user.save()
        print(f'User created: {user}')  # Debug output
        return user



class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    

    def validate(self, data):
        email = data.get('email')
        otp_code = data.get('otp_code')

        print(email)
        print(otp_code)

        # Check if the user with this email exists
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email does not exist.")

        # Check if an OTP for this user with the given code exists
        if not OTP.objects.filter(user__email=email, otp_code=otp_code).exists():
            raise serializers.ValidationError("Invalid OTP code.")

        return data
