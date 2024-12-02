# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from Accounts.models import *

# class DealerLoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')

#         if email and password:
#             user = authenticate(request=self.context.get('request'), email=email, password=password)
#             if user is None or not user.is_dealer:
#                 raise serializers.ValidationError("Invalid email or password.")
#         else:
#             raise serializers.ValidationError("Email and password are required.")

#         attrs['user'] = user
#         return attrs



# Define the serializer for validating login
class DealerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None or not user.is_dealer:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Email and password are required.")

        attrs['user'] = user
        return attrs


# class ServiceProviderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ServiceProvider
#         fields = '__all__'  # Or specify fields you want to include

from rest_framework import serializers
from Accounts.models import ServiceProvider, User  # Ensure you import User model

class ServiceProviderSerializer(serializers.ModelSerializer):
    # Custom field to get the full name from the User model
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = ServiceProvider
        fields = '__all__'  # Or specify fields explicitly if needed

    def get_full_name(self, obj):
        # Assuming 'full_name' is a field in the User model
        return obj.user.full_name if obj.user else None
    

class ServiceProviderPendingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = '__all__'  # or list specific fields

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


from rest_framework import serializers
from Accounts.models import ServiceProvider, ServiceRegister, CustomerReview

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRegister
        fields = '__all__'  # Or specify fields explicitly if needed


class PaymentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRequest
        fields = '__all__'
        read_only_fields = ['receiver', 'sernder']  # These are set in the view


class ServiceproviderSerializerSearch(serializers.ModelSerializer):
    # user = UserSerializer()

    name = serializers.CharField(source='user.full_name') 
    location=serializers.CharField(source='user.district')
    contact=serializers.IntegerField(source='user.phone_number')
    class Meta:
        model=ServiceProvider
        fields=['name','custom_id','verification_by_dealer','location','contact','status']


from Accounts.models import Franchisee, Franchise_Type

class FranchiseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Franchise_Type
        fields = ['name', 'details', 'amount', 'currency']  # Include the fields you want from Franchise_Type

class FranchiseSerializer(serializers.ModelSerializer):
    type = FranchiseTypeSerializer()  # Nest FranchiseTypeSerializer to get franchise type details

    class Meta:
        model = Franchisee
        fields = [
            'custom_id',
            'about',
            'profile_image',
            'revenue',
            'dealers',
            'service_providers',
            'type',  # Include the nested FranchiseTypeSerializer here
            'valid_from',
            'valid_up_to',
            'status',
            'verification_id',
            'verificationid_number',
            'community_name',
        ]



class DealerFranchiseeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Franchisee
        fields = [
            'custom_id', 'about', 'profile_image', 'revenue', 'dealers', 
            'service_providers', 'type', 'valid_from', 'valid_up_to', 
            'status', 'verification_id', 'verificationid_number', 
            'community_name', 'franchise_amount'
        ]


# Serializer for Ads model
class AdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ads
        fields = [
            'id', 'title', 'ad_type', 'amount', 
            'starting_date', 'ending_date', 'payment',
            'status', 'created'
        ]

# Enhanced ServiceSerializer to include basic stats
class ServiceSerializer(serializers.ModelSerializer):
    active_ads_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceRegister
        fields = [
            'id', 'description', 'gstcode', 'category',
            'subcategory', 'status', 'accepted_terms',
            'available_lead_balance', 'active_ads_count'
        ]

    def get_active_ads_count(self, obj):
        return obj.ads.filter(status='Active').count()