from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, OTP, Country_Codes, ServiceRequest
from django.core.mail import send_mail
from phonenumber_field.serializerfields import PhoneNumberField 
import pycountry 
import phonenumbers 
from rest_framework.exceptions import ValidationError
import random
import uuid


class UserRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False)  
    email = serializers.EmailField(required=False)
    country_code = serializers.CharField(max_length=10, required=False)  
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'country_code', 'password', 'confirm_password')

    def validate(self, attrs):
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        country_code = attrs.get('country_code')

        # Ensure either email or phone number is provided, but not both
        if not email and not phone_number:
            raise serializers.ValidationError("You must provide either an email or a phone number.")

        if email and phone_number:
            raise serializers.ValidationError("You can only provide one: either an email or a phone number, not both.")

        # Check if a user with the provided email already exists
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")

        # Validate the phone number if provided
        if phone_number and country_code:
            full_number = f"+{country_code}{phone_number.lstrip('0')}"  
            try:
                parsed_number = phonenumbers.parse(full_number, None)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise serializers.ValidationError("Invalid phone number format.")
                if User.objects.filter(phone_number=phone_number).exists():
                    raise serializers.ValidationError("A user with this phone number already exists.")
            except phonenumbers.NumberParseException:
                raise serializers.ValidationError("Invalid phone number.")

        # Validate the country_code exists in the Country_Codes model
        if country_code:
            # Remove leading '+' from the country code
            country_code = country_code.lstrip('+')

            if not country_code.isdigit():
                raise serializers.ValidationError("Country code must be numeric.")
    
            try:
                country_code_instance = Country_Codes.objects.get(calling_code=f"+{country_code}")
                attrs['country_code'] = country_code_instance  # Store the instance for later use
            except Country_Codes.DoesNotExist:
                raise serializers.ValidationError(f"Invalid country code: {country_code}")


        # Ensure passwords match
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match.")

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove confirm password from validated data
        phone_number = validated_data.get('phone_number')
        country_code_instance = validated_data.get('country_code')

        if phone_number:
            # Store the raw phone number (without the country code) directly
            phone_number = phone_number.lstrip('0')  # Strip leading zeros if necessary
            validated_data['phone_number'] = phone_number

        user = User.objects.create_user(**validated_data)  # Create user with validated data

        # Send OTP based on the provided contact method
        if validated_data.get('email'):
            self.send_otp_email(user, validated_data['email'])  
        elif validated_data.get('phone_number'):
            self.send_otp_sms(user, validated_data['phone_number'])  

        return user



    def send_otp_email(self, user, email):
        # Logic to send OTP to email
        otp = OTP.objects.create(user=user)  # Create OTP with the user instance
        send_mail(
            'Your OTP Code',
            f'Your OTP code is {otp.otp_code}',
            None,  # Uses DEFAULT_FROM_EMAIL from settings
            [email],  # Use email from the registration
            fail_silently=False,
        )

    def send_otp_sms(self, user, phone_number):
        # Logic to print OTP for phone number in the terminal (for now)
        otp = OTP.objects.create(user=user)  # Create OTP with the user instance
        print(f"Sending OTP: {otp.otp_code} to phone number: {phone_number}")

class OTPVerifySerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=6)

    def validate(self, data):
        otp_code = data.get('otp_code')

        # Find the OTP object using the provided otp_code
        try:
            otp_instance = OTP.objects.get(otp_code=otp_code)
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP code.")

        # Check if OTP has expired
        if otp_instance.is_expired():
            raise serializers.ValidationError("OTP has expired.")

        # Get the associated user from the OTP instance
        user = otp_instance.user

        # Mark the user as verified
        user.is_verified = True
        user.save()

        return {"message": "User verified successfully."}




#for service request and request views

class ServiceRequestSerializer(serializers.ModelSerializer):
    subcategory_title = serializers.CharField(source='service.subcategory.title', read_only=True)
    subcategory_id = serializers.IntegerField(source='service.subcategory.id', read_only=True)  # Get subcategory ID
    service_title = serializers.CharField(source='service.title', read_only=True)  # Get service title
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    service_provider_name = serializers.CharField(source='service_provider.full_name', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'customer_name',
            'service_provider_name',
            'service',  # Holds the service ID
            'service_title',  # Service title for output
            'subcategory_title',
            'subcategory_id',  # Subcategory ID for output
            'work_status',
            'acceptance_status',
            'availability_from',
            'availability_to',
            'additional_notes',
            'image',
            'booking_id',
            'description'  #not needed line
        ]
        read_only_fields = ['booking_id', 'customer', 'service', 'service_title', 'subcategory_title', 'subcategory_id']

class ServiceRequestDetailSerializer(serializers.ModelSerializer):
    subcategory_name = serializers.CharField(source='service.subcategory.title', read_only=True)
    service_title = serializers.CharField(source='service.title', read_only=True)  # Get service title
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'service_title',
            'subcategory_name',
            'customer_name',
            'availability_from',
            'availability_to',
            'acceptance_status'
        ]
