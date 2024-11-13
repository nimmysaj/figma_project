# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FranchiseeRegistrationSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from .serializers import FranchiseeLoginSerializer,ServiceProviderSerializer,DealerSerializer
from django.contrib.auth import get_user_model
from rest_framework import generics,permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from Accounts.models import ServiceProvider,Franchisee,Dealer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .permissions import IsFranchisee
import logging
from django.db import transaction


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
    
# class DealerCreateView(generics.CreateAPIView):
#     serializer_class = AdddealerSerializer
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exeption=True)

#         #usercreation
#         user = User.objects.create(
#              email = serializer.validate_data.get('email'),
#              phone_number = serializer.validate_data.get['phone_number'],
#              ful_name = serializer.validate_data.get['full_name'],
#              address = serializer.validate_data.get['address'],
#              pin_code = serializer.validate_data.get['pin_code'],
#              district = serializer.validate_data.get['district'],
#              state = serializer.validate_data.get['state'],
#              is_dealer=True

#         )

#         dealer = Dealer.objects.create(
#             user=user,
#             about = serializers.validate_data.get['about'],
#             profile_image = serializers.validate_data.get('profile_image'),
#             service_providers = serializers.validate_data.get('service_providers'),
#             franchisee = serializers.validate_data.get['franchisee'],
#             verification_id = serializers.validate_data.get('verification_id'),
#             verificationid_number = serializers.validate_data.get('verification_number'),
#             id_copy = serializers.validate_data.get('id_copy'),
#             status='Active'
#         )

#         return Response({'message': 'Dealer created successfully'}, status=status.HTTP_201_CREATED)


class DealerCreateView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is logged in

    def post(self, request):
        if not request.user.is_franchisee:
            return Response({"error": "Only franchisees can add dealers."}, status=status.HTTP_403_FORBIDDEN)

        serializer = DealerSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class DealerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ensure the logged-in user is a franchisee
        try:
            franchisee = Franchisee.objects.get(user=request.user)
        except Franchisee.DoesNotExist:
            return Response({"error": "Franchisee not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get all dealers under the logged-in franchisee
        dealers = Dealer.objects.filter(franchisee=franchisee)
        serializer = DealerSerializer(dealers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
