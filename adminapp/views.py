from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ServiceRequest
from .serializers import ServiceRequestSerializer
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserSerializer
from .pagination import CustomPagination


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


class UserDetailsView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        

class UserPaymentHistoryView(APIView):


    def post(self, request, format=None):
        users_id = request.data.get('users_id')
        
        if not users_id:
            return Response({"error": "User ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=users_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
class UserPaymentHistoryView(APIView):
    
        
    def post(self, request, *args, **kwargs):
        users_id = request.data.get('users_id')  # Get user ID from request data

        if not users_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Filter service requests for the specified user
        queryset =  User.objects.filter(id=users_id)

        # Apply pagination
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Serialize the paginated data
        serializer =UserSerializer(paginated_queryset, many=True)

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)