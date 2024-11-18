from rest_framework import serializers
from django.contrib.auth import authenticate
from Accounts.models import *


# Common Login Serializers for Customer,Service Provider,Dealer and Franchisee

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            print(email,password)
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if user is None:
                raise serializers.ValidationError("Invalid credentials.")
            if not (user.is_customer or user.is_service_provider or user.is_dealer or user.is_franchisee or user.is_superuser or user.is_staff):
                raise serializers.ValidationError("Invalid Email and Password.")
        else:
            raise serializers.ValidationError("Email and password are required.")

        attrs['user'] = user
        return attrs


from Accounts.models import ServiceProvider

class ServiceProviderVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = '__all__'

