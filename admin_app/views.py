from django.shortcuts import render
from rest_framework import permissions ,generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from rest_framework.permissions import IsAuthenticated
from Accounts.models import User, Franchise_Type ,Payment ,Franchisee
from .serializers import UserSerializer, FranchiseeSerializer ,TransactionSerializer


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

class TransactionPagination(PageNumberPagination):
    page_size = 10  # Number of items per page
    page_size_query_param = 'page_size'  # Allows clients to set the page size
    max_page_size = 100  # Maximum limit for page size


class FranchiseePaymentHistory(APIView):
    pagination_class = TransactionPagination

    def post(self, request):
        franchisee_id = request.data.get('franchisee_id')
        
        if not franchisee_id:
            return Response({"error": "franchisee_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch payments for the given franchisee
        payments = Payment.objects.filter(receiver__service_provider__franchisee__custom_id=franchisee_id) #Note : Using Franchisee Custom id to retrieve DATA

        # Paginate the queryset
        paginator = TransactionPagination()
        paginated_payments = paginator.paginate_queryset(payments, request)

        # Serialize the paginated data
        serializer = TransactionSerializer(paginated_payments, many=True)

        # Return paginated response
        return paginator.get_paginated_response(serializer.data)