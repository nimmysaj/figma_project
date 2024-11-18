from rest_framework import serializers
from Accounts.models import ServiceProvider
from service_provider.serializers import UserSerializer,ServiceRegisterSerializer
from Accounts.models import User
from rest_framework.exceptions import ValidationError

from django.contrib.auth import authenticate
from Accounts.models import *

class ServiceProviderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    services=ServiceRegisterSerializer(read_only=True,many=True)

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
            "accepted_terms",
            "services" 
            ]

    def create(self, validated_data):
        # Extract the nested user data from the validated data
        user_data = validated_data.pop('user')

        # Check if accepted_terms is False
        if not validated_data.get('accepted_terms'):
            raise ValidationError({"accepted_terms": "You must accept the terms and conditions to create a profile."})
        
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