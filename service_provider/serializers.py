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