from rest_framework import serializers
from .models import CustomerProfile

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['id', 'full_name', 'email', 'phone', 'gender', 'date_of_birth', 'address', 'house_name', 'landmark', 'pin_code', 'district', 'state']
