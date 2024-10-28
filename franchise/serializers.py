import re
from phonenumbers import NumberParseException, is_valid_number, parse
import phonenumbers
from rest_framework.response import Response
from rest_framework import serializers,status
from django.contrib.auth import authenticate
from Accounts.models import Franchisee,Franchise_Type,User,FranchiseeRegister,ServiceProvider
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password


# Franchisee Login Serializer
class FranchiseeLoginSerializer(serializers.Serializer):
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


# Forgot Password and Reset Password for Franchisee
class FranchiseePasswordForgotSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True)

    def validate_email_or_phone(self, value):
        if '@' in value:
            if not User.objects.filter(email=value, is_franchisee=True).exists():
                raise serializers.ValidationError("This email is not registered with any franchisee.")
        else:
            if not User.objects.filter(phone_number=value, is_franchisee=True).exists():
                raise serializers.ValidationError("This phone number is not registered with any franchisee.")
        return value    


class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs


# Franchisee Profile Updation
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
            'whatsapp',
            'email',
            'country_code',
            'phone_number'
        ]


class FranchiseeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Franchisee
        fields = [
            "user",
            "custom_id"
            "profile_image",
            "revenue", 
            "dealer",
            "service_providers",
            "type",
            "valid_from",
            "valid_up_tp",
            "status",
            "verification_id"
            "verificationid_number"
            "community_name"
        ]

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        if not validated_data.get('accepted_terms'):
            raise ValidationError({"accepted_terms": "You must accept the terms and conditions to create a profile."})

        user = User.objects.create(**user_data)
        franchisee = Franchisee.objects.create(user=user, **validated_data)
        return franchisee

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        instance.save()
        return instance


# Franchisee Service Registration and Viewing of Registered Services
class FranchiseeRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = FranchiseeRegister
        fields = ['id', 'franchisee', 'description', 'gstcode', 'category', 'subcategory', 'license', 'image', 'status', 'accepted_terms', 'available_lead_balance']

    def validate(self, data):
        franchisee = data.get('franchisee')
        if franchisee.verification_by_dealer != 'APPROVED':
            raise serializers.ValidationError("Franchisee must be approved by the dealer to register the service.")
        if franchisee.status != 'Active':
            raise serializers.ValidationError("Franchisee must be active to register the service.")
        return data


# Franchisee Service Register Update and Lead Balance
class FranchiseeRegisterUpdateSerializer(serializers.ModelSerializer):
    add_lead = serializers.IntegerField(required=False)

    class Meta:
        model = FranchiseeRegister
        fields = ['description', 'gstcode', 'status', 'accepted_terms', 'add_lead']

    def update(self, instance, validated_data):
        add_lead = validated_data.pop('add_lead', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        #if instance.subcategory and instance.subcategory.collar:
           # lead_quantity = instance.subcategory.collar.lead_quantity
           # collar_amount = instance.subcategory.collar.amount

            #if instance.subcategory.service_type.name == "Daily Work" and add_lead is not None:
               # raise serializers.ValidationError({"message": "You have unlimited leads. No need to add or adjust lead balance."})

            #if add_lead is not None:
             #   total_lead_quantity = lead_quantity * add_lead
             #   instance.available_lead_balance += total_lead_quantity
             #   amount_to_paid = collar_amount * add_lead
             #   self.context['total_lead_quantity'] = total_lead_quantity
              #  self.context['amount_to_paid'] = amount_to_paid

        instance.save()
        return instance
class ServiceProviderSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    franchise_name = serializers.CharField(source='franchisee.franchise_name', read_only=True)

    class Meta:
        model = ServiceProvider
        fields = [
            'photo', 'full_name', 'date_of_birth', 'email', 'phone_number', 'password',
            'franchise_name', 'gender', 'house_name', 'landmark', 'pincode', 'district', 
            'state', 'verification_id', 'verification_number', 'verification_type'
        ]

    def validate(self, attrs):
        # Validate that the password meets complexity requirements (optional)
        password = attrs.get('password')
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return attrs

    def create(self, validated_data):
        franchisee = self.context['request'].user.franchisee  # Franchisee making the request

        # Pop password from validated data and create user
        password = validated_data.pop('password')
        user = User.objects.create(
            username=validated_data['email'],
            email=validated_data['email'],
            password=make_password(password),
            is_active=True,
        )
        
        # Create the ServiceProvider linked to the franchisee and user
        service_provider = ServiceProvider.objects.create(
            franchisee=franchisee,
            **validated_data
        )
        return service_provider