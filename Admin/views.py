from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from Accounts.models import ServiceRequest
from .serializers import ServiceRequestDetailSerializer
from rest_framework.exceptions import NotFound
from customer.permissions import IsOwnerOrAdmin
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class CustomerServiceRequestsView(APIView):
    
    permission_classes = [] 

    """
    API View to get all service requests for a particular customer.
    """

    def get(self, request, servicerequest_id, *args, **kwargs):
        """
        Get all service requests for the given customer ID, along with associated complaints, invoices, and reviews.
        """
        # Filter ServiceRequests by servicerequest_id
        try:
           
            service_requests = ServiceRequest.objects.filter(id=servicerequest_id)  
            
        except ServiceRequest.DoesNotExist:
            raise NotFound("Service requests not found for the given servicerequest ID.")
        
        # Serialize the service requests along with their nested data
        serializer = ServiceRequestDetailSerializer(service_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)