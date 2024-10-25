from django.shortcuts import render
from Accounts.models import *  # Ensure you import your models


# Create your views here.

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


# from django.shortcuts import get_object_or_404
# from rest_framework import generics
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.permissions import IsAuthenticated
# from .serializers import ServiceProviderSerializer

# from django.shortcuts import get_object_or_404

# class DealerServiceProviderListView(generics.ListAPIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer_class = ServiceProviderSerializer

#     def get_queryset(self):
#         user = self.request.user  # This is a User instance
#         print(f"User: {user}, Type: {type(user)}, Is Dealer: {user.is_dealer}")  # Added Is Dealer check
#         dealer = get_object_or_404(Dealer, user=user)
#         print(f"Dealer: {dealer}, Type: {type(dealer)}")  # Print dealer details

#         return ServiceProvider.objects.filter(dealer=dealer)


from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter  # Add SearchFilter import
from Accounts.models import ServiceProvider, Dealer  # Ensure you import Dealer model
from .serializers import ServiceProviderSerializer

class DealerServiceProviderListView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceProviderSerializer
    filter_backends = [SearchFilter]  # Enable search functionality
    search_fields = ['user__full_name', 'user__phone_number', 'user__district__name']  # Define search fields

    def get_queryset(self):
        user = self.request.user  # Get the logged-in user
        dealer = get_object_or_404(Dealer, user=user)  # Ensure the user is a dealer
        return ServiceProvider.objects.filter(dealer=dealer)  # Filter by dealer



from rest_framework import generics
from rest_framework.filters import SearchFilter  # Correct import for SearchFilter
from .serializers import ServiceproviderSerializerSearch
from .serializers import *

class SearchAPIView(generics.ListCreateAPIView):
    search_fields = ['user__full_name', 'user__phone_number', 'user__district__name']  # Correct fields
    filter_backends = (SearchFilter,)  # Use SearchFilter directly
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceproviderSerializerSearch
