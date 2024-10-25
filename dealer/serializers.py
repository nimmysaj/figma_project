# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from Accounts.models import *

class DealerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
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



class ServiceproviderSerializerSearch(serializers.ModelSerializer):
    # user = UserSerializer()

    name = serializers.CharField(source='user.full_name') 
    location=serializers.CharField(source='user.district')
    contact=serializers.IntegerField(source='user.phone_number')
    class Meta:
        model=ServiceProvider
        fields=['name','custom_id','verification_by_dealer','location','contact','status']