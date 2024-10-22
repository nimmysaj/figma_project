import re
from phonenumbers import NumberParseException, is_valid_number, parse
import phonenumbers
from rest_framework.response import Response
from rest_framework import serializers,status
from django.contrib.auth import authenticate
from Accounts.models import Invoice, ServiceProvider, ServiceRequest, User, Payment,CustomerReview 
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError

#service provider login
class ServiceProviderLoginSerializer(serializers.Serializer):
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

class PaymentListSerializer(serializers.ModelSerializer): 
    invoice_type = serializers.CharField(source='invoice.invoice_type', read_only=True) 
    class Meta: 
        model = Payment 
        fields = ['transaction_id', 'sender', 'receiver', 'invoice_type', 'payment_status']

class CustomerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerReview
        fields = ['id', 'rating', 'image', 'comment', 'created_at', 'customer', 'service_provider','service_request']