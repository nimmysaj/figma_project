from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ServiceRequest
from .serializers import ServiceRequestSerializer
from django.shortcuts import get_object_or_404


class ServiceRequestDetailView(APIView):
    def post(self, request, *args, **kwargs):
        
        service_request_id = request.data.get('service_request_id')

        
        if not service_request_id:
            return Response({"error": "Service request ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        
        service_request = get_object_or_404(ServiceRequest, id=service_request_id)

        # Serialize the service request, including the related invoices, reviews, and complaints
        serializer = ServiceRequestSerializer(service_request)

        # Return the serialized data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)