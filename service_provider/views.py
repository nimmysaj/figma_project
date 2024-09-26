from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from Accounts.models import ServiceProvider
from service_provider.serializers import serviceProviderSerialzer

class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset =ServiceProvider.objects.all()
    serializer_class = serviceProviderSerialzer
    #permission_class =[IsAuthenticated]


