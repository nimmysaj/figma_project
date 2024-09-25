from rest_framework import serializers
from Accounts.models import User, OTP

class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email_or_phone = data.get('email_or_phone')
        password = data.get('password')

        # Check if email_or_phone is email or phone number
        if '@' in email_or_phone:
            user = User.objects.filter(email=email_or_phone).first()
        else:
            user = User.objects.filter(phone_number=email_or_phone).first()

        if not user:
            raise serializers.ValidationError('Invalid credentials')

        # Check if password is valid
        if not user.check_password(password):
            raise serializers.ValidationError('Invalid password')

        # Check user role
        if not user.is_customer:
            raise serializers.ValidationError('You are not allowed to log in')

        data['user'] = user
        return data

class ForgotPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']  # Assuming the User model has an email field

class VerifyOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['otp_code']

class NewPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password']

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

