from rest_framework import serializers
from Accounts.models import ServiceProvider

class serviceProviderSerialzer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = "__all__"