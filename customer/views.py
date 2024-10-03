from rest_framework.views import APIView
from django.shortcuts import render
from django.core import signing
from django.contrib.auth.tokens import default_token_generator
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status,generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from Accounts.models import User, OTP,Category,Subcategory,ServiceProvider,ServiceRegister
from .serializers import ForgotPasswordSerializer, VerifyOTPSerializer, NewPasswordSerializer,LoginSerializer,CategorySerializer,SubcategorySerializer,ServiceProviderSerializer
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from django.db.models import Avg



class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(status='active')  # Only active categories
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        category = self.get_object()
        # Fetch only active subcategories
        subcategories = Subcategory.objects.filter(category=category, status='active')
        serializer = SubcategorySerializer(subcategories, many=True)
        return Response(serializer.data)



class SubcategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subcategory.objects.filter(status='active')  # Only active subcategories
    serializer_class = SubcategorySerializer
    permission_classes = [IsAuthenticated]

   

class SubcategoryServiceProviders(APIView):
    def get(self, request, subcategory_id):
        # Fetch the active service providers linked to the specific subcategory
        service_providers = ServiceProvider.objects.filter(
            status='Active',
            verification_by_dealer='APPROVED',
            services__subcategory_id=subcategory_id,  # Filtering by subcategory_id
            services__status='Active'
        ).annotate(
            rating=Avg('user__to_review__rating')  # Correctly referencing the CustomerReview through the User model
        ).values(
            'user__full_name',  # Service provider's name
            'services__amount_forthis_service',  # Service amount
            'rating'  # Average rating
        )

        # Return the response
        return Response(service_providers)




class LoginView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        if serializer.is_valid():
            user= serializer.validated_data['user']
            refresh=RefreshToken.for_user(user)
            access=refresh.access_token
            return Response({
                'message':"login successful",
                'refresh':str(refresh),
                'access':str(access)
            }, status=status.HTTP_200_OK)
        else :
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes=[AllowAny]
    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid():
            user= serializer.validated_data['user']
            otp = OTP.objects.create(user=user, expires_at=timezone.now() + timezone.timedelta(minutes=5))
            #otp sending code goes here
            print(otp.otp_code)
            return Response({"message": "OTP sent."}, status=status.HTTP_200_OK)
        else :
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes=[AllowAny]
    def post(self, request):
        otp_code = request.data.get('otp_code')
        try:
            otp = OTP.objects.get(otp_code=otp_code)
            if otp.is_expired():
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'message': 'OTP verified successfully',
                'resetToken': default_token_generator.make_token(otp.user),
                'userId' : signing.dumps(otp.user.id)
            }, status=status.HTTP_200_OK)
        except OTP.DoesNotExist:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

class NewPasswordView(generics.UpdateAPIView):
    serializer_class = NewPasswordSerializer
    permission_classes=[AllowAny]
    def post(self, request):
        reset_token = request.data.get('resetToken')
        new_password = request.data.get('newPassword')
        user_id=request.data.get('userId')
        user=User.objects.get(id=signing.loads(user_id))
        is_valid = default_token_generator.check_token(user, reset_token)


        if is_valid:
            serial=self.serializer_class(user,data={'password':new_password})
            if serial.is_valid() :
                serial.save()
                return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

