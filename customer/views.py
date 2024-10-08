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
from Accounts.models import User, OTP,Category,Subcategory,ServiceProvider,ServiceRegister,CustomerReview
from .serializers import ForgotPasswordSerializer, VerifyOTPSerializer, NewPasswordSerializer,LoginSerializer,CategorySerializer,SubcategorySerializer,ServiceProviderSerializer
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from django.db.models import Avg,F



class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(status='Active')  # Only active categories
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class SubcategoryViewSet(APIView):
    queryset = Subcategory.objects.filter(status='Active')  # Only active subcategories
    serializer_class = SubcategorySerializer
    permission_classes = [IsAuthenticated]
    def post(self, request):
        category_id = request.data.get("category_id")
        if not category_id:
            return Response({"error":"category_id field required"},status=status.HTTP_400_BAD_REQUEST)
        try:
            category=Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error":"category_id does not match any category"},status=status.HTTP_400_BAD_REQUEST)
        subcategories = self.queryset.filter(category=category)
        serializer = self.serializer_class(subcategories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





class SubcategoryServiceProviders(APIView):
    queryset = ServiceRegister.objects.filter(status='Active')  # Only active subcategories
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request):
        subcategory_id = request.data.get("subcategory_id")
        subcategory=Subcategory.objects.get(id=subcategory_id)
        services = self.queryset.filter(subcategory=subcategory)
        services.annotate(
            user_name=F("service_provider__user__full_name"),
            rating=Avg("service_provider__user__to_review__rating"),
            amount=Avg("servicerequest__invoices__total_amount")
        )
        serializer = self.serializer_class(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



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
        
class ResendOTP(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes=[AllowAny]
    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid():
            user= serializer.validated_data['user']
            otp = OTP.objects.get(user=user)
            #otp sending code goes here
            print(otp.otp_code)
            return Response({"message": "OTP resent."}, status=status.HTTP_200_OK)
        else :
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

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

