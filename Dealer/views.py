from django.shortcuts import render

# Create your views here.
from Accounts.models import ServiceProvider
from Dealer.serializers import ServiceProviderSerializer,DealerLoginSerializer
from rest_framework import generics
from rest_framework import filters

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
# from django.contrib.auth import authenticate,
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated




# get the list of all non verified service providers under the logged in dealer     
class ServiceProviderVerificationListView(generics.ListAPIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    serializer_class=ServiceProviderSerializer
    filter_backends=[filters.SearchFilter]
    search_fields=['user__full_name','user__district__name']
    def get_queryset(self):
        user = self.request.user
        return ServiceProvider.objects.filter(
            verification_by_dealer='PENDING', 
            accepted_terms=True, 
            dealer__user=user
        )



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
            'token': token.key, # Include the token in the response
            'user_id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'is_dealer': user.is_dealer,
        }, status=status.HTTP_200_OK)
    
