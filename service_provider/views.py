from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from Accounts.models import ServiceProvider, User
from service_provider.serializers import ServiceProviderSerialzer, UserSerializer

class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset =ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerialzer
    #permission_class =[IsAuthenticated]


