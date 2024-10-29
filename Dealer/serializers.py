from rest_framework import serializers
from django.contrib.auth import authenticate
from Accounts.models import *

class PaymentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRequest
        fields = [
            'full_name', 'contact_number', 'email_address', 'payment_method',
            'account_holder_name', 'bank_name', 'bank_branch', 'account_number',
            'ifsc_code', 'amount', 'supporting_documents', 'reason'
        ]
        read_only_fields = ['status']  # Status is initially set to 'Pending'

    def create(self, validated_data):
        validated_data['status'] = 'Pending'  # Default to Pending status
        return super().create(validated_data)
