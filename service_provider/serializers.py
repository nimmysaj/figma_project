import re
from phonenumbers import NumberParseException, is_valid_number, parse
import phonenumbers
from rest_framework.response import Response
from rest_framework import serializers,status
from django.contrib.auth import authenticate
from Accounts.models import Invoice, ServiceProvider, ServiceRequest, User, Payment,AdCategory,AdManagement 
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

    sender_full_name = serializers.CharField(source='sender.full_name', read_only=True)
    receiver_full_name = serializers.CharField(source='receiver.full_name', read_only=True)
    invoice_type = serializers.CharField(source='invoice.invoice_type', read_only=True)
    
    class Meta:
        model = Payment
        fields = [ 
            'transaction_id',
            'sender_full_name',  
            'receiver_full_name',
            'invoice_type',
            'payment_status',
            'amount_paid',
            
        ]


# class BoostServiceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AdManagement
#         fields = ['id', 'service_name', 'boost_service_image','valid_from', 'valid_up_to', 
#                   'target_area', 'total_days', 'total_amount','ad_category', ]

#     def create(self, validated_data):
       
#         request_user = self.context['request'].user
#         if not request_user.is_authenticated:
#             raise ValidationError("User must be authenticated")

#         # Calculate the total number of days 
#         valid_from = validated_data['valid_from']
#         valid_up_to = validated_data['valid_up_to']
#         total_days = (valid_up_to - valid_from).days

#         #  calculate the total amount based on the rate and category
#         ad_category = validated_data['ad_category']
#         total_amount = total_days * ad_category.rate

#         # Create the AdManagement instance
#         ad_instance = AdManagement.objects.create(
#             **validated_data,
#             total_days=total_days,
#             total_amount=total_amount
#         )




class BoostServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdManagement
        fields = ['id', 'title','description','service_name', 'boost_service_image', 'valid_from', 'valid_up_to', 
                  'target_area', 'total_days', 'total_amount', 'ad_category']

    def create(self, validated_data):
        # Ensure that the user is authenticated
        request_user = self.context['request'].user
        if not request_user.is_authenticated:
            raise ValidationError("User must be authenticated")

        # Calculate the total number of days
        valid_from = validated_data['valid_from']
        valid_up_to = validated_data['valid_up_to']
        total_days = (valid_up_to - valid_from).days

        # Get the ad category (which contains boost_service)
        ad_category = validated_data['ad_category']

        # Ensure the selected category is 'boost_service' before calculating the rate
        if ad_category.ad_type != 'boost_service':
            raise ValidationError("The ad category must be of type 'Boost Service'")

        # Get the rate for the boost service category
        boost_service_rate = ad_category.rate

        # Calculate the total amount based on the rate and total_days
        total_amount = total_days * boost_service_rate

        # Add the calculated values to validated_data
        validated_data['total_days'] = total_days
        validated_data['total_amount'] = total_amount

        # Create the AdManagement instance (specific to boosting service)
        ad_instance = AdManagement.objects.create(**validated_data)

        return ad_instance