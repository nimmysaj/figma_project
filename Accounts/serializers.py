from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User, ServiceProviderProfile

class ServiceProviderLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)
        if user is None or not user.is_service_provider:
            raise serializers.ValidationError('Invalid credentials')
        attrs['user'] = user
        return attrs
    
class ServiceProviderPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_service_provider=True).exists():
            raise serializers.ValidationError("Email not registered")
        return value
    
class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
        