from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from Accounts.models import ServiceProviderProfile
from service_provider.serializer import ServiceProviderSerializer



class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProviderProfile.objects.all()
    serializer_class = ServiceProviderSerializer
