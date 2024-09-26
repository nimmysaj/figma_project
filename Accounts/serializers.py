from rest_framework import serializers
from django.contrib.auth import authenticate
from Accounts.models import User  

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


class ServiceProviderPasswordResetSerializer(serializers.Serializer):
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

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
