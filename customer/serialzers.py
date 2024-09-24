from rest_framework import serializers
from Accounts.models import Category,Subcategory

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'image' , 'description' , 'status']
class SubcategorySerialzer(serializers.ModelSerializer):
    class Meta:
        model=Subcategory
        fields=['id','title','category','image','description','service_type','collar','status']