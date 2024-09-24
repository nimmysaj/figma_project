from rest_framework import serializers
from .models import Category, SubCategory, Service, ServiceProvider

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'image' , 'description' , 'status']