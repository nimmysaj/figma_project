import re
from rest_framework import serializers
from django.utils import timezone
from Accounts.models import User, OTP
from django.conf import settings
from django.core.mail import send_mail

class ServiceProviderRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        """
        Check if password and confirm_password match.
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        # return data
        
        if len(data['password']) < 8:
           raise serializers.ValidationError(
                           {'error_field':'password',
                           'status_code':400,
                           'message' : 'The length password should contain atleast 8 characters.'})
        if not re.findall('[A-Z]', data['password']):
           raise serializers.ValidationError(
                           {'error_field':'password',
                           'status_code':400,
                           "message" : "The password must contain at least 1 uppercase letter, A-Z."})
        if not re.findall('[a-z]', data['password']):
           raise serializers.ValidationError(
                           {'error_field':'password',
                           'status_code':400,
                           'message' : 'The password must contain at least 1 lowercase letter, a-z.'})
        if not re.findall('[0-9]', data['password']):
           raise serializers.ValidationError(
                           {'error_field':'password',
                           'status_code':400,
                           'message' : 'The password must contain at least 1 number (0-9).'})
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', data['password']):
           raise serializers.ValidationError(
                           {'error_field':'password',
                           'status_code':400,
                           'message' : 'Your password must contain at least 1 symbol. '})
        if data['password'] != data['confirm_password']:
           raise serializers.ValidationError(
                           {'error_field':'confirm_password',
                           'status_code':400,
                           'message' : 'Your password and confirmation password do not match.'})
      
        return data



    def create(self, validated_data):
        # Remove confirm_password as it's not needed to create the user
        validated_data.pop('confirm_password')

        # Create the user
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            is_service_provider=True
        )
        user.set_password(validated_data['password'])
        user.save()

        # Create a service provider profile for the user
        # ServiceProviderProfile.objects.create(user=user)

        # Generate OTP and send it to email
        otp = OTP.objects.create(
            user=user,
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        self.send_otp_email(user.email, otp.otp_code)
        
        return user

    def send_otp_email(self, email, otp_code):
        subject = 'Your OTP Code'
        message = f'Your OTP code is {otp_code}. It will expire in 10 minutes.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        send_mail(subject, message, from_email, recipient_list)


class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp_code = data.get('otp_code')

        try:
            user = User.objects.get(email=email)
            otp = OTP.objects.get(user=user, otp_code=otp_code)
        except (User.DoesNotExist, OTP.DoesNotExist):
            raise serializers.ValidationError("Invalid OTP or email.")

        if otp.is_expired():
            raise serializers.ValidationError("OTP has expired.")

        return data

    def verify_otp(self):
        # Activate the user after OTP verification
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        user.is_active = True  # Mark the user as active
        user.save()