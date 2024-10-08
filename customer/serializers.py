from rest_framework import serializers
from Accounts.models import User, OTP
import re
from django.core.validators import RegexValidator,EmailValidator
from django.core.exceptions import ValidationError
from rest_framework import serializers
from Accounts.models import Category,Subcategory,ServiceProvider,CustomerReview,ServiceRegister
from django.db.models import Avg

phone_regex = RegexValidator(
    regex=r'^\d{9,15}$',  
    message="Phone number must be between 9 and 15 digits."
)

class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)
    email_validator = EmailValidator()

    def validate_email_or_phone(self, value):
        
        if '@' in value:
            # Validate email format using EmailValidator
            self.email_validator(value)  # Validate email
        else:
            # Validate phone number format using RegexValidator
            try:
                phone_regex(value)  # Validate phone number
            except ValidationError:
                raise serializers.ValidationError("Invalid phone number format.")
        return value
    
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

class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True)
    email_validator = EmailValidator()

    def validate_email_or_phone(self, value):
        
        if '@' in value:
            # Validate email format using EmailValidator
            self.email_validator(value)  # Validate email
        else:
            # Validate phone number format using RegexValidator
            try:
                phone_regex(value)  # Validate phone number
            except ValidationError:
                raise serializers.ValidationError("Invalid phone number format.")
        return value
    
    def validate(self, data):
        email_or_phone = data.get('email_or_phone')

        # Check if email_or_phone is email or phone number
        if '@' in email_or_phone:
            user = User.objects.filter(email=email_or_phone).first()
        else:
            user = User.objects.filter(phone_number=email_or_phone).first()

        if not user:
            raise serializers.ValidationError('Invalid credentials')

        

        # Check user role
        if not user.is_customer:
            raise serializers.ValidationError('Not a customer account')

        data['user'] = user
        return data

class VerifyOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['otp_code']

class NewPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password']
    def validate_password(self, value):
        # Enforce minimum length (e.g., 8 characters)
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        # Ensure the password contains at least one uppercase letter
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")

        # Ensure the password contains at least one lowercase letter
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")

        # Ensure the password contains at least one digit
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")

        # Ensure the password contains at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'status']

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'title', 'category', 'description', 'service_type', 'status']


class ServiceProviderSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='service_provider.user.full_name', read_only=True)
    rating = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRegister
        fields = ['id','user_name', 'rating', 'amount']
    def get_rating(self,obj):
        return obj.service_provider.user.to_review.aggregate(Avg('rating'))['rating__avg']
    def get_amount(self,obj):
        serReq=obj.servicerequest.all()
        if serReq.exists():
            return obj.servicerequest.all().first().invoices.aggregate(Avg('total_amount'))['total_amount__avg']
        else:
            return None




class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[phone_regex])

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'address', 'pin_code', 'district', 'state', 'phone_number', 'country_code', 'is_customer']

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
