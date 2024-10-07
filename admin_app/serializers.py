from rest_framework import serializers
from Accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ['email','full_name','nationality','designation','phone_number','is_active','is_staff']
        fields = '__all__'
        