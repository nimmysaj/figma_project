from rest_framework import serializers
from .models import Category, Subcategory, Service_Type, Collar, ServiceProvider


# Serializer for creating/updating subcategories
class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'title', 'image', 'description', 'service_type', 'collar', 'status', 'category']

# Serializer for creating/updating categories
class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'image', 'description', 'status', 'subcategories']


# Serializer for Service_Type
class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service_Type
        fields = ['id', 'name', 'details']

# Serializer for Collar
class CollarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collar
        fields = ['id', 'name', 'lead_quantity', 'amount', 'currency']

# Serializer for Service_Provider
class ServiceProviderSerializer(serializers.ModelSerializer):
    subcategory = serializers.PrimaryKeyRelatedField(queryset=Subcategory.objects.all())
    
    class Meta:
        model = ServiceProvider
        fields = ['id', 'name', 'subcategory', 'description', 'contact_info']