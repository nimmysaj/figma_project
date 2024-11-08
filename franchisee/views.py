# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FranchiseeRegistrationSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from .serializers import FranchiseeLoginSerializer,ServiceProviderSerializer
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from Accounts.models import ServiceProvider,Franchisee
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .permissions import IsFranchisee


class FranchiseeRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FranchiseeRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Franchisee registered successfully",
                "user_id": user.id,
                "email": user.email
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Token pair view (access + refresh)
class CustomTokenObtainPairView(TokenObtainPairView):
    # Customize if you need to modify the response
    pass

# Token refresh view
class CustomTokenRefreshView(TokenRefreshView):
    # Customize if you need to modify the response
    pass

User = get_user_model()

class FranchiseeLoginView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this endpoint (no authentication required)

    def post(self, request):
        serializer = FranchiseeLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            if not user.is_franchisee:
                return Response(
                    {"error": "User is not a franchisee"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Get or create token for the authenticated franchisee
            # token, created = Token.objects.get_or_create(user=user)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            return Response({
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": str(refresh),
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceProviderCreateAPIView(generics.CreateAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsFranchisee] 

    def get_serializer_context(self):
        # Automatically set the authenticated user as the franchisee
        return {'request': self.request}