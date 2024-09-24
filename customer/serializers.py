from rest_framework import serializers
from .models import CustomerProfile

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['full_name', 'address', 'date_of_birth', 'gender', 'house_name', 'landmark', 'pin_code', 'district', 'state']
        # read_only_fields = ['full_name']


