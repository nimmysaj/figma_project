from rest_framework import serializers
from .models import Category, Subcategory, ServiceProvider, Complaint
from customer.models import Customer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'status']

class SubCategorySerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category', 'icon', 'status']


class ServiceProviderSerializer(serializers.ModelSerializer):
    subcategory = serializers.PrimaryKeyRelatedField(queryset=Subcategory.objects.all())
    class Meta:
        model = ServiceProvider
        fields = ['id', 'name', 'subcategory', 'description', 'contact_info', 'status']

class ComplaintSerializer(serializers.ModelSerializer):
    custom_id = serializers.CharField(write_only=True)

    class Meta:
        model = Complaint
        fields = ['id', 'service_provider', 'title', 'description', 'custom_id']  # Include custom_id here

    def create(self, validated_data):
        custom_id = validated_data.pop('custom_id', None)  # Get custom_id from the validated data
        customer = Customer.objects.filter(custom_id=custom_id).first()
        
        if not customer:
            raise serializers.ValidationError('Customer with the provided custom_id does not exist')
        
        # Create the complaint using the customer instance
        complaint = Complaint.objects.create(customer=customer, **validated_data)
        return complaint
