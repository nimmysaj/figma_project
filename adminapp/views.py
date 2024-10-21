from django.views import generic
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .models import ServiceRequest
from .serializers import ServiceRequestSerializer
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserSerializer
from .pagination import CustomPagination
from .models import Category, Subcategory
from  .serializers import CategorySerializer


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
    

@api_view(['GET', 'POST'])
def category_list(request):
    # Handle GET request
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)

        # Prepare custom response with counts
        response_data = {
            'total_categories': Category.objects.count(),
            'total_subcategories': Subcategory.objects.count(),  # Assuming Subcategory model exists
            'categories': serializer.data  # Include the actual list of categories
        }

        return Response(response_data)  # This is reachable now

    # Handle POST request
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT', 'PATCH', 'DELETE'])
def category_detail(request):
    # Get the 'id' from the request body.
    category_id = request.data.get('id')

    if not category_id:
        return Response({"error": "ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)