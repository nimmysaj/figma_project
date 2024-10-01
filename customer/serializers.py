import re
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from app1.models import Customer
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email_or_phone = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    
    
    class Meta:
        model = User
        fields = ['email_or_phone', 'password', 'confirm_password']
    
    def validate_new_password(self, value):
        # Use Django's built-in password validators to validate the password
        validate_password(value)

        # Custom validation for password complexity
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")

        return value

    def validate(self, data):
        email_or_phone = data.get('email_or_phone')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Check if both passwords match
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")

        # Validate email or phone number format
        if '@' in email_or_phone:
            # Check if email is already registered
            if User.objects.filter(email=email_or_phone).exists():
                raise serializers.ValidationError("Email is already in use")
        else:
            # Check if phone number is already registered
            if User.objects.filter(phone_number=email_or_phone).exists():
                raise serializers.ValidationError("Phone number is already in use")

        return data

    def create(self, validated_data):
        email_or_phone = validated_data.get('email_or_phone')
        password = validated_data.get('password')

        # Create user based on whether email or phone is provided
        if '@' in email_or_phone:
            user = User.objects.create_user(email=email_or_phone, password=password)
        else:
            user = User.objects.create_user(phone_number=email_or_phone, password=password)
        
        # Ensure that is_customer is always set to True during registration
        user.is_active = False  # User is inactive until OTP is verified
        user.is_customer = True
        user.save()

        if user.is_customer:
            Customer.objects.create(user=user)

        return user
    

class CustomerLoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        password = attrs.get('password')

        # Validate that either email or phone and password are provided
        if not email_or_phone:
            raise serializers.ValidationError('Email or phone is required.')
        if not password:
            raise serializers.ValidationError('Password is required.')

        # Try to authenticate the user using email or phone number
        user = None
        if '@' in email_or_phone:
            # If input is email
            user = authenticate(username=email_or_phone, password=password)
        else:
            # If input is phone number
            try:
                user = User.objects.get(phone_number=email_or_phone)
                if not user.check_password(password):
                    raise serializers.ValidationError('Invalid credentials.')
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid login credentials.')

        if user is None or not user.is_customer:
            raise serializers.ValidationError('Invalid login credentials or not a customer.')

        attrs['user'] = user
        return attrs    
    
class CustomerPasswordForgotSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True)

    def validate_email_or_phone(self, value):
        """
        This function will check if the provided value is either a valid email or a phone number.
        For now, we assume the input is either an email or phone number.
        """
        if '@' in value:
            # Validate as email
            if not User.objects.filter(email=value, is_customer=True).exists():
                raise serializers.ValidationError("This email is not registered with any customer.")
        else:
            # Validate as phone number
            if not User.objects.filter(phone_number=value, is_customer=True).exists():
                raise serializers.ValidationError("This phone number is not registered with any customer.")

        return value    


class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate_password(self, value):
        # Use Django's password validators to validate the password
        validate_password(value)

        # Custom validation for password complexity
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")


        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'full_name',
            'address', 
            'landmark',
            'pin_code',
            'district',
            'state',
            'watsapp',
            'email',
            'country_code',
            'phone_number'
            ]
        
class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = [ "user",
            "profile_image",
            "date_of_birth",
            "gender" 
            ]

    def create(self, validated_data):
        # Extract the nested user data from the validated data
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        service_provider = Customer.objects.create(user=user, **validated_data)
        return service_provider

    def update(self, instance, validated_data):
        # Extract user data and handle separately
        user_data = validated_data.pop('user', None)

        # Update ServiceProvider fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle User fields separately
        if user_data:
            user = instance.user  # Get the related user instance
            for attr, value in user_data.items():
                if attr == 'email' and user.email:
                    continue  # Skip updating email if it's already set
                if attr == 'phone_number' and user.phone_number:
                    continue  # Skip updating phone number if it's already set
                setattr(user, attr, value)
            user.save()

        # Save the ServiceProvider instance with updated data
        instance.save()
        return instance

