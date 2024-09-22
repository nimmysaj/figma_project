


from rest_framework import serializers
from Accounts.models import ServiceProviderProfile

class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProviderProfile
        fields = '__all__'
