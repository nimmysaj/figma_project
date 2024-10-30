from rest_framework import serializers
from Accounts.models import Dealer

class DealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealer
        fields = [
            'user', 
            'custom_id', 
            'about', 
            'profile_image', 
            'service_providers', 
            'franchisee', 
            'status', 
            'verification_id', 
            'verificationid_number', 
            'id_copy'
        ]
        read_only_fields = ['custom_id']