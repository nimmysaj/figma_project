from django.shortcuts import render

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
