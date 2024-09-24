from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status,generics
from rest_framework.response import Response
from .serialzers import CategorySerializer
from Accounts.models import Category

class GetCategoriesView(APIView):
    serializer_class = CategorySerializer
    def get(self,request):
        output=Category.objects.filter(status='Active')
        serial=self.serializer_class(output,many=True)
        return Response(serial.data,status=status.HTTP_200_OK)
