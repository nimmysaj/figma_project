from rest_framework import serializers
from .models import Category, Subcategory, ServiceProvider, Complaint

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
    class Meta:
        model = Complaint
        fields = ['id', 'service_provider', 'title', 'description', 'additional_requirements', 'status', 'created_at', 'images']
