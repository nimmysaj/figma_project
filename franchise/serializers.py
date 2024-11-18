from rest_framework import serializers
from django.contrib.auth import authenticate
from Accounts.models import *


# class FranchiseeLoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')

#         if email and password:
#             user = authenticate(request=self.context.get('request'), email=email, password=password)
#             if user is None or not user.is_franchisee:
#                 raise serializers.ValidationError("Invalid email or password.")
#         else:
#             raise serializers.ValidationError("Email and password are required.")

#         attrs['user'] = user
#         return attrsfrom rest_framework import serializers
from Accounts.models import Dealer,Franchisee,User
from django.contrib.auth import authenticate



    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
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
        read_only_fields=['id','email','phone_number']

class DealerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    franchise_name = serializers.CharField(source='franchisee.user.full_name', read_only=True)
    dealer_id=serializers.CharField(write_only=True)
    class Meta:
        model = Dealer
        fields = [
            'dealer_id',
            'user',
            'custom_id',
            'about',
            'profile_image',
            'service_providers',
            'franchisee',
            'franchise_name',
            'status',
            'verification_id',
            'verificationid_number',
            'id_copy'
        ]
        read_only_fields = ['custom_id']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user

        # Check for unique email
        if User.objects.filter(email=user_data.get('email')).exclude(id=user.id).exists():
            user_data.pop('email')
            

        # Update user fields
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # Update Dealer fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
