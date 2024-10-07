from rest_framework import serializers
from Accounts.models import User
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']
        # fields = ['id','last_login','is_customer','is_service_provider','is_franchisee','is_dealer','is_active','email','full_name','nationality','designation','phone_number','is_active','is_staff']
        # fields = '__all__'

        
        