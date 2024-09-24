from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status,generics
from rest_framework.response import Response
from .serialzers import CategorySerializer,SubcategorySerialzer
from Accounts.models import Category,Subcategory

class GetCategoriesView(APIView):
    serializer_class = CategorySerializer
    def get(self,request):
        try:
            output=Category.objects.filter(status='Active')
            serial=self.serializer_class(output,many=True)
            return Response(serial.data,status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'message':'Category Does not Exist'},status=status.HTTP_404_NOT_FOUND)
class GetSubcategoryView(APIView):
    serializer_class=CategorySerializer
    def get(self,request):
        Category_id=request.data.get('Category_id')
        try:
            category=Category.objects.get(id=Category_id)
            output=Subcategory.objects.filter(status='Active',category=category)
            serial=self.serializer_class(output,many=True)
            return Response(serial.data,status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'message':'Category Does not Exist'},status=status.HTTP_404_NOT_FOUND)
        except Subcategory.DoesNotExist:
            return Response({'message':'Subcategory Does not Exist'},status=status.HTTP_404_NOT_FOUND)
   
