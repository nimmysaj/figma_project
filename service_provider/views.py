from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from Accounts.models import Complaint, Service_Type, Collar, Category, Subcategory, ServiceRegister
from .serializers import  ComplaintSerializer, ServiceRegisterSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

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
    

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    # permission_classes = [IsAuthenticated]

    # Custom action for service provider to accept or reject a complaint
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        complaint = self.get_object()
        user = request.user
        print(user)

        # Check if the requesting user is the service provider for this complaint
        # if complaint.service_provider != user:
        #     raise PermissionDenied("You do not have permission to update the status of this complaint.")

        # Get the new status and reason from the request data
        new_status = request.data.get('status')
        reason = request.data.get('resolution_notes')

        # Ensure valid status update
        if new_status not in ['in_progress', 'resolved', 'rejected']:
            return Response({'detail': 'Invalid status provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the complaint status and reason
        complaint.status = new_status
        complaint.resolution_notes = reason

        if new_status == 'resolved':
            complaint.resolved_at = timezone.now()  # Set resolved time if resolved

        complaint.save()

        # Return success response with the updated details
        return Response({
            'detail': f'Complaint status updated to {new_status}.',
            'reason': reason
        }, status=status.HTTP_200_OK)