from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions 
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from Accounts.models import ServiceProvider, Complaint
from service_provider.serializers import ComplaintSerializer, ComplaintCreateSerializer
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone 
from rest_framework.decorators import action



class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    # permission_classes = [IsAuthenticated]  
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ComplaintCreateSerializer
        return ComplaintSerializer
    def perform_create(self, serializer):
        serializer.save()  



    @action(detail=False, methods=['get'], url_path='active')
    def list_active_complaints(self, request):
        """List all active complaints."""
        active_complaints = self.queryset.filter(status__in=['pending', 'in_progress'])
        serializer = self.get_serializer(active_complaints, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='completed')
    def list_completed_complaints(self, request):
        """List all completed complaints."""
        completed_complaints = self.queryset.filter(status='resolved')
        serializer = self.get_serializer(completed_complaints, many=True)
        return Response(serializer.data)
