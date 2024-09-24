from rest_framework import serializers
from Accounts.models import ServiceType, Collar, Category, Subcategory, ServiceRegister





class ServiceRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRegister
        fields = '__all__'
