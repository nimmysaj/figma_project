from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from Accounts.models import ServiceProvider
from .serializers import ServiceProviderVerificationSerializer

class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderVerificationSerializer