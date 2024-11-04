from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import FranchiseeLoginSerializer
from Accounts.models import Franchisee, PaymentRequest, Complaint, ServiceRequest
from franchise.serializers import FranchiseeSerializer, PaymentRequestSerializer, ServiceRequestSerializer, ComplaintSerializer
from rest_framework import generics, permissions
from django.contrib.auth import authenticate
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404


class FranchiseeLoginView(generics.GenericAPIView):
    serializer_class = FranchiseeLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate a token for the authenticated user
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'message': 'Login successful',
            'token': token.key,  # Include the token in the response
            'user_id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'is_franchisee': user.is_franchisee,
        }, status=status.HTTP_200_OK)



# To list the  details of the logged-in franchisee

class FranchiseeListView(generics.ListAPIView):
    serializer_class = FranchiseeSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated

    def get_queryset(self):
        # Get the logged-in franchisee
        franchise = Franchisee.objects.get(user=self.request.user)
        # Return the corresponding details of this franchisee
        return Franchisee.objects.filter(id=franchise.id)
    



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Set the default page size
    page_size_query_param = 'page_size'  # Allow clients to set the page size
    max_page_size = 100 



# To list the transaction history of franchisee

class FranchisePaymentHistoryView(generics.ListAPIView):
    serializer_class = PaymentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            # Get the logged-in franchisee
            franchise = Franchisee.objects.get(user=self.request.user)
            # Return payment requests associated with the service providers linked to this franchisee
            return PaymentRequest.objects.filter(service_provider__franchisee=franchise).order_by('-created_at')
        except Franchisee.DoesNotExist:
            raise NotFound("Franchisee not found.")
    



class FranchiseeComplaintsListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        # Get the logged-in franchisee
        franchisee = Franchisee.objects.get(user=self.request.user)
        
        # Filter complaints related to the franchisee
        return Complaint.objects.filter(
            sender=franchisee.user
        ).union(
            Complaint.objects.filter(receiver=franchisee.user)
        ).order_by('-submitted_at')
    


class IncompleteBookingsListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ServiceRequestSerializer

    def get_queryset(self):
        # Get the logged-in franchisee
        franchisee = get_object_or_404(Franchisee, user=self.request.user)
        
        # Get the service providers related to the franchisee
        service_providers = franchisee.serviceprovider_set.all()
        
        # Get the user IDs of the service providers
        service_provider_users = [provider.user.id for provider in service_providers]
        
        # Filter for incomplete bookings based on user IDs
        return ServiceRequest.objects.filter(
            service_provider__id__in=service_provider_users,
            work_status__in=['pending', 'in_progress']
        ).order_by('-request_date')