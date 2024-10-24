from django.shortcuts import render
from rest_framework import permissions ,generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from Accounts.models import User ,Payment ,Franchisee ,Service_Type ,Collar
from .serializers import UserSerializer, FranchiseeSerializer ,TransactionSerializer ,CollarSerializer ,ServiceTypeSerializer
from rest_framework.views import APIView



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Change based on your requirements
    def get_permissions(self):
        if self.action == 'create':  
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super(UserViewSet, self).get_permissions() 
        
        
# Franchisee ViewSet
class FranchiseeViewSet(viewsets.ModelViewSet):
    queryset = Franchisee.objects.all()
    serializer_class = FranchiseeSerializer
    permission_classes = [IsAuthenticated]  # Change based on your requirements

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

# class TransactionsListView(generics.ListAPIView):
#     queryset = Payment.objects.all()
#     serializer_class = TransactionSerializer

# class TransactionDetailView(generics.RetrieveAPIView):
#     queryset = Payment.objects.all()
#     serializer_class = TransactionSerializer


# class FranchiseePaymentHistory(APIView):
#     pagination_class = TransactionPagination

#     def post(self, request):
#         franchisee_id = request.data.get('franchisee_id')
        
#         if not franchisee_id:
#             return Response({"error": "franchisee_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
#         payments = Payment.objects.filter(invoice__service_request__service_provider__franchisee__custom_id=franchisee_id) #Note : Using Franchisee Custom id to retrieve DATA

#         # Paginate the queryset
#         paginator = TransactionPagination()
#         paginated_payments = paginator.paginate_queryset(payments, request)

#         # Serialize the paginated data
#         serializer = TransactionSerializer(paginated_payments, many=True)

#         # Return paginated response
#         return paginator.get_paginated_response(serializer.data)



class TransactionPagination(PageNumberPagination):
    page_size = 10  # Number of items per page
    page_size_query_param = 'page_size'  # Allows clients to set the page size
    max_page_size = 100  # Maximum limit for page size

class TransactionListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = TransactionSerializer
    pagination_class = TransactionPagination


# TASK 3 SERVICE TYPE CRUD //////////////////////////////////////////////////////////////////////////////////////////////////

class ServiceTypeAPIView(APIView):
    
    def post(self, request):
        """Create a new service type with validation."""
        serializer = ServiceTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Retrieve a specific service type by ID or get all if no ID is provided."""
        service_id = request.data.get('id')
        
        if service_id:
            try:
                service = Service_Type.objects.get(id=service_id)
                serializer = ServiceTypeSerializer(service)
                return Response(serializer.data)
            except Service_Type.DoesNotExist:
                return Response({"error": "Service type not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # If no ID is provided, return all service types.
            services = Service_Type.objects.all()
            serializer = ServiceTypeSerializer(services, many=True)
            return Response(serializer.data)

    def put(self, request):
        """Update a service type (replace all fields)."""
        service_id = request.data.get('id')
        if not service_id:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service_Type.objects.get(id=service_id)
            serializer = ServiceTypeSerializer(service, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Service_Type.DoesNotExist:
            return Response({"error": "Service type not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        """Partially update a service type."""
        service_id = request.data.get('id')
        if not service_id:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service_Type.objects.get(id=service_id)
            serializer = ServiceTypeSerializer(service, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Service_Type.DoesNotExist:
            return Response({"error": "Service type not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        """Delete a service type."""
        service_id = request.data.get('id')
        if not service_id:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service_Type.objects.get(id=service_id)
            service.delete()
            return Response({"message": "Service type deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Service_Type.DoesNotExist:
            return Response({"error": "Service type not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
# TASK 3 Collor CRUD //////////////////////////////////////////////////////////////////////////////////////////////////


class CollarAPIView(APIView):

    def post(self, request):
        """Create a new collar."""
        serializer = CollarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Retrieve a specific collar by ID or all collars if no ID is provided."""
        collar_id = request.data.get('id')
        if collar_id:
            try:
                collar = Collar.objects.get(id=collar_id)
                serializer = CollarSerializer(collar)
                return Response(serializer.data)
            except Collar.DoesNotExist:
                return Response({"error": "Collar not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            collars = Collar.objects.all()
            serializer = CollarSerializer(collars, many=True)
            return Response(serializer.data)

    def put(self, request):
        """Fully update a collar."""
        collar_id = request.data.get('id')
        if not collar_id:
            return Response({"error": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            collar = Collar.objects.get(id=collar_id)
            serializer = CollarSerializer(collar, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Collar.DoesNotExist:
            return Response({"error": "Collar not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        """Partially update a collar."""
        collar_id = request.data.get('id')
        if not collar_id:
            return Response({"error": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            collar = Collar.objects.get(id=collar_id)
            serializer = CollarSerializer(collar, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Collar.DoesNotExist:
            return Response({"error": "Collar not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        """Delete a collar."""
        collar_id = request.data.get('id')
        if not collar_id:
            return Response({"error": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            collar = Collar.objects.get(id=collar_id)
            collar.delete()
            return Response({"message": "Collar deleted."}, status=status.HTTP_204_NO_CONTENT)
        except Collar.DoesNotExist:
            return Response({"error": "Collar not found."}, status=status.HTTP_404_NOT_FOUND)