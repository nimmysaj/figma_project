from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from Accounts.models import Customer
from .serializers import CustomerSerializer
from .serializers import Customerview_Serializer

from .pagination import CustomerViewPagination

# Create your views here.




# ********************  ADD NEW USER *********************

class UserCreateView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def perform_create(self, serializer):
        # Auttomatically set is_customer = True in the serializer 
        serializer.save()





# ************************  USERS-USER MANAGEMENT  ************************* 

class CustomerListView(generics.ListAPIView):
    queryset = Customer.objects.all()             # Fetch all customers
    serializer_class = Customerview_Serializer
    pagination_class = CustomerViewPagination    # Apply custom pagination



