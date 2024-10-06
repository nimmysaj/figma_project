from rest_framework import serializers
from .models import Franchise_Type
import re

class Franchise_Type_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Franchise_Type  # Specify the model to be serialized
        fields = ['id', 'name', 'details', 'amount', 'currency']

     # Field-level validation for 'name'
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("The name must be at least 3 characters long.")
        if len(value) > 50:
            raise serializers.ValidationError("The name must not exceed 50 characters.")
        if re.search(r'\d', value):
            raise serializers.ValidationError("The name must not contain numbers.")
        return value

     # Field-level validation for 'amount'
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("The amount must be greater than 0.")
        if value > 1000000:
            raise serializers.ValidationError("The amount must not exceed 1,000,000.")
        return value

    # Field-level validation for 'currency'
    def validate_currency(self, value):
        allowed_currencies = ['USD', 'EUR', 'INR', 'GBP', 'AUD', 'CAD', 'JPY', 'CNY', 'CHF', 'SGD']
        if value not in allowed_currencies:
            raise serializers.ValidationError(f"Currency must be one of {allowed_currencies}.")
        return value