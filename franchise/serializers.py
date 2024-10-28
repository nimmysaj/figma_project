import re
from django.contrib.auth.hashers import make_password
from phonenumbers import NumberParseException, is_valid_number, parse
import phonenumbers
from rest_framework.response import Response
from rest_framework import serializers,status
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
import logging
from rest_framework import serializers
from Accounts.models import *
from django_filters import rest_framework as filters
from django.contrib.auth.hashers import make_password

class ServiceProviderListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source= 'user.full_name')
    id = serializers.CharField()
    registered_services = serializers.IntegerField(source= 'services.count', read_only = True)
    active_jobs = serializers.SerializerMethodField()
    status = serializers.CharField()
    contacts = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(write_only= True)


    class Meta:
        model = ServiceProvider
        fields = ['name', 'id', 'registered_services', 'active_jobs', 'status', 'contacts', 'district', 'created_at',]

    def get_contacts(self, obj):
        return{
            "phone_number": obj.user.phone_number,
            "email": obj.user.email
        }    
    def get_district(self, obj):
        return obj.user.district.name if obj.user.district else None
    
    def get_active_jobs(self, obj):
        return ServiceRequest.objects.filter(
            service_provider = obj.user,
            acceptance_status = "accept",
            work_status = 'in_progress'
        ).count()
       
# franchise login    
logger = logging.getLogger(__name__)
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

        user = None

        # Look up user by email or phone
        if '@' in email_or_phone:
            try:
                user = User.objects.get(email=email_or_phone)
                logger.debug(f"Found franchisee by email: {user.email}")
            except User.DoesNotExist:
                raise serializers.ValidationError('No account found with this email.')
        else:
            try:
                fullnumber = phonenumbers.parse(email_or_phone, None)
                code = Country_Codes.objects.get(calling_code="+" + str(fullnumber.country_code))
                number = str(fullnumber.national_number)
                
                user = User.objects.get(phone_number=number, country_code=code)
                logger.debug(f"Found franchisee by phone: {user.email}")
            except (phonenumbers.phonenumberutil.NumberParseException, Country_Codes.DoesNotExist):
                raise serializers.ValidationError('Invalid phone number format.')
            except User.DoesNotExist:
                raise serializers.ValidationError('No account found with this phone number.')

        # Validate franchisee status
        if not user.is_active:
            raise serializers.ValidationError('This account is inactive.')
        if not user.is_franchisee:
            raise serializers.ValidationError('This account is not registered as a franchisee.')

        # Check password
        if not user.check_password(password):
            logger.debug(f"Password verification failed for franchisee: {user.email}")
            raise serializers.ValidationError('Invalid password.')

        logger.debug("Franchisee authentication successful.")
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
            is_active=True,)






# class ServiceProviderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ServiceProvider
#         fields = ['id', 'name', 'email', 'phone', 'address', 'services_offered']



#             is_active=True,
#         )
        
#         # Create the ServiceProvider linked to the franchisee and user
#         service_provider = ServiceProvider.objects.create(
#             franchisee=franchisee,
#             **validated_data
#         )
#         return service_provider
#                 raise serializers.ValidationError('Invalid phone number format.')
#             except User.DoesNotExist:
#                 raise serializers.ValidationError('No account found with this phone number.')

#         # Validate franchisee status
#         if not user.is_active:
#             raise serializers.ValidationError('This account is inactive.')
#         if not user.is_franchisee:
#             raise serializers.ValidationError('This account is not registered as a franchisee.')

#         # Check password
#         if not user.check_password(password):
#             logger.debug(f"Password verification failed for franchisee: {user.email}")
#             raise serializers.ValidationError('Invalid password.')

#         logger.debug("Franchisee authentication successful.")
#         attrs['user'] = user
#         return attrs