from rest_framework import serializers
from Accounts.models import ServiceProviderVerification

class ServiceProviderVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProviderVerification
        fields = '__all__'
