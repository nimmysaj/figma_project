from rest_framework import serializers
from Accounts.models import User, OTP
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
import random

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)  
    phone_number = serializers.CharField(required=False)  
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'phone_number']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
        }

    def validate(self, data):
        # Check for at least one of email or phone number
        if not data.get('email') and not data.get('phone_number'):
            raise serializers.ValidationError("Either email or phone number must be provided.")

        # Validate email if provided
        if data.get('email') and User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists.")
        
        # Validate phone number if provided
        if data.get('phone_number') and User.objects.filter(phone_number=data['phone_number']).exists():
            raise serializers.ValidationError("Phone number already exists.")

        # Check that both password fields match
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Passwords do not match."})

        return data

    def create(self, validated_data):
        validated_data.pop('password2')  # Remove password2 since it's not needed anymore
        user = User(**validated_data)
        user.set_password(validated_data['password'])  # Hash password
        user.save()

        
        otp_code = str(random.randint(100000, 999999))

        
        otp_instance = OTP.objects.create(
            user=user,
            otp_code=otp_code,
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )

        # Determine whether to send OTP via email or SMS
        if 'email' in validated_data:
            self.send_email(validated_data['email'], otp_instance.otp_code)
        elif 'phone_number' in validated_data:
            # Temporarily print OTP to console instead of sending SMS
            print(f"Your OTP code is {otp_instance.otp_code}. It will expire in 10 minutes.")
            # self.send_sms(validated_data['phone_number'], otp_instance.otp_code)

        return user

    # def send_email(self, email, otp_code):
    #     send_mail(
    #         subject='Your OTP Code for Registration',
    #         message=f"Your OTP code is {otp_code}. It will expire in 10 minutes.",
    #         from_email='youremailid',
    #         recipient_list=[email],
    #     )

    # def send_sms(self, phone_number, otp_code):
    #     account_sid = ''
    #     auth_token = ''
    #     client = Client(account_sid, auth_token)

    #     message = client.messages.create(
    #         body=f"Your OTP code is {otp_code}. It will expire in 10 minutes.",
    #         from_='YOUR_TWILIO_PHONE_NUMBER',
    #         to=phone_number
    #     )
    #     return message.sid



from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist  
# from rest_framework_simplejwt.tokens import RefreshToken  

class OTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)  
    phone_number = serializers.CharField(required=False)  

    class Meta:
        model = OTP
        fields = ['email', 'phone_number', 'otp_code']  

    def validate(self, attrs):
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        otp_code = attrs.get('otp_code').strip().upper()  

        if email and phone_number:
            raise serializers.ValidationError("Please provide either email or phone number, not both.")

        user = None
        if email:
            try:
                user = User.objects.get(email=email)  
            except User.DoesNotExist:
                raise serializers.ValidationError("User with this email does not exist.")
        elif phone_number:
            try:
                user = User.objects.get(phone_number=phone_number)  
            except User.DoesNotExist:
                raise serializers.ValidationError("User with this phone number does not exist.")
        else:
            raise serializers.ValidationError("Email or phone number must be provided.")

        otp_instance = OTP.objects.filter(
            user=user,
            otp_code=otp_code
        ).first()

        if not otp_instance:
            raise serializers.ValidationError("Invalid OTP code")

        if otp_instance.is_expired():
            raise serializers.ValidationError("OTP has expired")

        otp_instance.delete()  
        attrs['user'] = user  
        return attrs

    # def generate_jwt_token(self, user):
    #     refresh = RefreshToken.for_user(user)
    #     return {
    #         'refresh': str(refresh),
    #         'access': str(refresh.access_token),
    #     }            