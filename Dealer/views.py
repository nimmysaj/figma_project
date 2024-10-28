from django.shortcuts import render
<<<<<<< HEAD

# Create your views here.
from Accounts.models import ServiceProviderVerification
from .serializers import ServiceProviderVerificationSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import DealerLoginSerializer

class DealerLoginView(generics.GenericAPIView):
    serializer_class = DealerLoginSerializer

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
            'is_dealer': user.is_dealer,
        }, status=status.HTTP_200_OK)

# List and Create View
class ServiceProviderVerificationListCreate(generics.ListCreateAPIView):
    queryset = ServiceProviderVerification.objects.all()
    serializer_class = ServiceProviderVerificationSerializer

# Retrieve, Update, Delete View
class ServiceProviderVerificationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceProviderVerification.objects.all()
    serializer_class = ServiceProviderVerificationSerializer
from django.shortcuts import render

# Create your views here.
from Accounts.models import ServiceProvider
from Dealer.serializers import ServiceProviderSerializer,DealerLoginSerializer
from rest_framework import generics
from rest_framework import filters

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
=======
from rest_framework import generics, permissions
from rest_framework.response import Response
from Accounts.models import Dealer, Franchisee, PaymentRequest
from Dealer.serializers import FranchiseeSerializer, PaymentRequestSerializer
from rest_framework.pagination import PageNumberPagination
>>>>>>> mybranch




<<<<<<< HEAD
# get the list of all non verified service providers under the logged in dealer     
class ServiceProviderVerificationListView(generics.ListAPIView):
    queryset=ServiceProvider.objects.filter(verification_by_dealer='PENDING',accepted_terms=True,dealer=1)
    serializer_class=ServiceProviderSerializer
    filter_backends=[filters.SearchFilter]
    search_fields=['user__full_name','user__district__name']
    def get_queryset(self):
        user = self.request.user
        return ServiceProvider.objects.filter(
            verification_by_dealer='PENDING', 
            accepted_terms=True, 
            dealer=user
        )

=======

# To list the franchisee details of the logged-in dealer

class DealerFranchiseeListView(generics.ListAPIView):
    serializer_class = FranchiseeSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated

    def get_queryset(self):
        # Get the logged-in dealer
        dealer = Dealer.objects.get(user=self.request.user)
        # Return the corresponding franchisee for this dealer
        return Franchisee.objects.filter(id=dealer.franchisee.id)
    




class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Set the default page size
    page_size_query_param = 'page_size'  # Allow clients to set the page size
    max_page_size = 100 



# To list the transaction history of dealer

class DealerPaymentHistoryView(generics.ListAPIView):
    serializer_class = PaymentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        dealer = Dealer.objects.get(user=self.request.user)
        # Return the payment requests associated with this dealer
        return PaymentRequest.objects.filter(dealer=dealer).order_by('-created_at')
>>>>>>> mybranch
