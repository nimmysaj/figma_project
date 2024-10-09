from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'profile_image', 'custom_id', 'full_name', 'address', 'date_of_birth', 'gender', 'house_name', 'landmark', 'pin_code', 'district', 'state']
        read_only_fields = ['status']

    def create(self, validated_data):
        # Retrieve the user from the context
        user = self.context.get('user')  # Get user from context (or handle accordingly)
        
        # Create the Customer instance with user and other validated data
        customer = Customer.objects.create(user=user, **validated_data)
        
        return customer