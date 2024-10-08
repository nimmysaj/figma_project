from rest_framework import serializers
from Accounts.models import ServiceProvider, Complaint


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            'id', 'service_provider', 'service_request', 'subject', 'description', 
            'images', 'submitted_at', 'status', 
            'resolved_at', 'resolution_notes'
        ]
        read_only_fields = ['id', 'submitted_at', 'status', 'resolved_at']

class ComplaintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['service_provider', 'customer','service_request', 'subject', 'description', 'images']


