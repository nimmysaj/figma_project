from rest_framework import serializers
from Accounts.models import ServiceProvider,ServiceRegister
from service_provider.serializers import UserSerializer
from Accounts.models import User
from rest_framework.exceptions import ValidationError

from django.contrib.auth import authenticate
from Accounts.models import *
from django.db.models import Count



from rest_framework import serializers
from Accounts.models import ServiceProvider, ServiceRegister, ServiceRequest

class ServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = ['id', 'booking_id', 'title', 'customer', 'work_status', 'acceptance_status', 'request_date', 'availability_from', 'availability_to', 'additional_notes', 'image']

class ServiceRegisterSerializer(serializers.ModelSerializer):
    total_orders = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRegister
        fields = ['id', 'description', 'category', 'subcategory', 'image', 'total_orders']

    def get_total_orders(self, obj):
        return ServiceRequest.objects.filter(service=obj).count()

class ServiceProviderSerializer(serializers.ModelSerializer):
    services = ServiceRegisterSerializer(many=True, read_only=True)
    user = UserSerializer()
    dealer=serializers.CharField(source='dealer.user.full_name')
    franchisee=serializers.CharField(source='franchisee.user.full_name')

    class Meta:
        model = ServiceProvider
        fields = ['user', 'custom_id', 'profile_image', 'about','verification_by_dealer', 'dealer', 'franchisee','services']


# Common Login Serializers for Customer,Service Provider,Dealer and Franchisee



class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        email = attrs.get('email')

        password = attrs.get('password')

        if email and password:

            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if user is None:

                raise serializers.ValidationError("Invalid credentials.")

            if not (user.is_customer or user.is_service_provider or user.is_dealer or user.is_franchisee or user.is_superuser or user.is_staff):

                raise serializers.ValidationError("Invalid Email and Password.")

        else:

            raise serializers.ValidationError("Email and password are required.")

        attrs['user'] = user
        return attrs