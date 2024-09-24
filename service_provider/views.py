from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from Accounts.models import ServiceType, Collar, Category, Subcategory, ServiceRegister
from .serializers import  ServiceRegisterSerializer
from django.shortcuts import get_object_or_404

class ServiceRegisterViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = ServiceRegister.objects.all()
        serializer = ServiceRegisterSerializer(queryset, many=True)
        return Response({"message": "Service Registers retrieved successfully.", "data": serializer.data}, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = ServiceRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Service Register created successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": "Failed to create Service Register.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(ServiceRegister, pk=pk)
        serializer = ServiceRegisterSerializer(instance)
        return Response({"message": "Service Register details retrieved successfully.", "data": serializer.data}, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        instance = get_object_or_404(ServiceRegister, pk=pk)
        serializer = ServiceRegisterSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Service Register updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": "Failed to update Service Register.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        instance = get_object_or_404(ServiceRegister, pk=pk)
        instance.delete()
        return Response({"message": "Service Register deleted successfully."}, status=status.HTTP_204_NO_CONTENT)