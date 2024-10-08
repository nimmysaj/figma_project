from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status, permissions
from Accounts.models import Complaint, Service_Type, Collar, Category, ServiceProvider, Subcategory, ServiceRegister, User
from .serializers import  ComplaintSerializer,  ServiceRegisterSerializer,ServiceRegisterUpdateSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

class ServiceRegisterViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = ServiceRegister.objects.all()
    serializer_class = ServiceRegisterSerializer

    def list(self, request):
        # Assuming the service provider ID is passed as a query parameter (e.g., ?service_provider=1)
        service_provider_id = request.query_params.get('service_provider')
        
        if service_provider_id:
            # Filter by the provided service provider ID
            queryset = ServiceRegister.objects.filter(service_provider_id=service_provider_id)
        else:
            # Optionally return an empty result or all services (depending on the requirements)
            return Response({
                "message": "Service provider ID is required.",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the filtered queryset
        serializer = ServiceRegisterSerializer(queryset, many=True)
    
        return Response({
            "message": "Service Registers retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


    def create(self, request):
        serializer = ServiceRegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            service_provider_id = serializer.validated_data.get('service_provider')
            
            # Retrieve the service provider and check if their status is 'Active'
            service_provider = get_object_or_404(ServiceProvider, id=service_provider_id.id)

            if service_provider.status != 'Active':
                return Response({
                    "message": "Service provider is not active. Cannot register service.",
                    "errors": {"service_provider": "Service provider must be active to register services."}
                }, status=status.HTTP_400_BAD_REQUEST)

            # Save the service registration if the service provider is active
            serializer.save()
            return Response({
                "message": "Service Register created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": "Failed to create Service Register.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(ServiceRegister, pk=pk)
        serializer = ServiceRegisterSerializer(instance)
        return Response({"message": "Service Register details retrieved successfully.", "data": serializer.data}, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """
        Update the ServiceRegister instance (no lead balance update here).
        """
        instance = get_object_or_404(ServiceRegister, pk=pk)
        
        # Update the ServiceRegister instance using the serializer
        serializer = ServiceRegisterUpdateSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Service Register updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        # Handle invalid serializer
        return Response({
            "message": "Failed to update Service Register.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='add-lead-balance')
    def add_lead_balance(self, request, pk=None):
        """
        Custom action to increment lead balance for 'One Time Lead' services.
        """
        instance = get_object_or_404(ServiceRegister, pk=pk)

        # Check if the subcategory service type is "One Time Lead"
        if instance.subcategory.service_type.name == 'One Time Lead':
            # Increment the lead balance using the collar's lead quantity
            instance.update_lead_balance()
            
            # Return the collar amount after updating lead balance
            return Response({
                "message": "Lead balance updated successfully.",
                "available_lead_balance": instance.available_lead_balance,
                "collar_amount": instance.subcategory.collar.amount
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "Lead balance can only be updated for 'One Time Lead' services.",
            }, status=status.HTTP_400_BAD_REQUEST)

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
    
