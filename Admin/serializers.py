# serializers.py
from rest_framework import serializers
from Accounts.models import Franchisee, Franchise_Type


class FranchiseeSerializer(serializers.ModelSerializer):
    franchisee_type = serializers.StringRelatedField(source='type.name')  # To show franchisee type name instead of ID

    class Meta:
        model = Franchisee
        fields = '__all__'  # Or you can specify fields like ['custom_id', 'user', 'status', 'valid_from', 'franchisee_type']
from rest_framework import serializers
from Accounts.models import Franchisee, Franchise_Type

class FranchiseeSerializer(serializers.ModelSerializer):
    # Custom field to display username or franchisee name
    franchisee_name = serializers.CharField(source='user.full_name', read_only=True)  
    franchisee_type = serializers.StringRelatedField(source='type.name')  # To show franchisee type name instead of ID

    class Meta:
        model = Franchisee
        fields = '__all__' 

