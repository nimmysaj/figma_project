import re
from phonenumbers import NumberParseException, is_valid_number, parse
import phonenumbers
from rest_framework import serializers
from django.contrib.auth import authenticate
from app1.models import ServiceProvider, User  
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

class ServiceProviderLoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        password = attrs.get('password')

        if not email_or_phone:
            raise serializers.ValidationError('Email or phone is required.')
        if not password:
            raise serializers.ValidationError('Password is required.')

        user = authenticate(username=email_or_phone, password=password)
        if user is None:
            try:
                user = User.objects.get(phone_number=email_or_phone)  
                if not user.check_password(password):
                    user = None
            except User.DoesNotExist:
                user = None

        if user is None:
            raise serializers.ValidationError('Invalid login credentials.')

        attrs['user'] = user
        return attrs



class ServiceProviderPasswordForgotSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True)

    def validate_email_or_phone(self, value):
        """
        This function will check if the provided value is either a valid email or a phone number.
        For now, we assume the input is either an email or phone number.
        """
        if '@' in value:
            # Validate as email
            if not User.objects.filter(email=value, is_service_provider=True).exists():
                raise serializers.ValidationError("This email is not registered with any service provider.")
        else:
            # Validate as phone number
            if not User.objects.filter(phone_number=value, is_service_provider=True).exists():
                raise serializers.ValidationError("This phone number is not registered with any service provider.")

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
        
class ServiceProviderSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ServiceProvider
        fields = [ "user",
            "profile_image",
            "date_of_birth",
            "gender" ,
            "dealer",
            "franchisee",
            "address_proof_document",
            "id_number", 
            "address_proof_file" ,
            "payout_required", 
            "accepted_terms" 
            ]

    def create(self, validated_data):
        # Extract the nested user data from the validated data
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        service_provider = ServiceProvider.objects.create(user=user, **validated_data)
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

