from rest_framework import serializers
from Accounts.models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'image' , 'description' , 'status']