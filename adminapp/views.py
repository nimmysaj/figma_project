from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from Accounts.models import Customer
from .serializers import CustomerSerializer

# Create your views here.

class UserCreateView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def perform_create(self, serializer):
        # Auttomatically set is_customer = True in the serializer 
        serializer.save()
