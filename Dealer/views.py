from django.shortcuts import render

# Create your views here.

from rest_framework import generics
from Accounts.models import ServiceProviderVerification
from .serializers import ServiceProviderVerificationSerializer

# List and Create View
class ServiceProviderVerificationListCreate(generics.ListCreateAPIView):
    queryset = ServiceProviderVerification.objects.all()
    serializer_class = ServiceProviderVerificationSerializer

# Retrieve, Update, Delete View
class ServiceProviderVerificationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceProviderVerification.objects.all()
    serializer_class = ServiceProviderVerificationSerializer
