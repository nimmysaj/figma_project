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
 
    # def retrieve(self, request, *args, **kwargs):
    #     try:
    #         profile = self.get_object()
    #         serializer = self.get_serializer(profile)
    #         return Response(serializer.data)
    #     except ServiceProviderProfile.DoesNotExist:
    #         return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # @action(detail=False, methods=['get'])
    # def profile_by_id(self, request):
    #     profile_id = request.query_params.get('id')
    #     profile = ServiceProviderProfile.objects.filter(id=profile_id).first()
    #     if profile:
    #         serializer = self.get_serializer(profile)
    #         return Response(serializer.data)
    #     else:
    #         return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
 