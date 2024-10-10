from rest_framework import serializers
from .models import ServiceRequest
from .models import ServiceRegister

class ServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = '__all__'
        
class ServiceregisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRegister
        fields = '__all__'
