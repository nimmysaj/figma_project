from rest_framework import serializers
from Accounts.models import ServiceRegister

class ServiceRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRegister
        fields = [
            'id', 'service_name', 'description', 'gstcode', 'category', 
            'subcategory', 'license', 'image', 'status', 'accepted_terms', 
            'available_lead_balance'
        ]
