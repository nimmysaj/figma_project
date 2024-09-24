from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status,generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from Accounts.models import User, OTP
from .serializers import ForgotPasswordSerializer, VerifyOTPSerializer, NewPasswordSerializer
from django.utils import timezone


# Create your views here.

class LoginView(APIView):
    def post(self,request):
        try:
            user=User.objects.get(username=request.data.get('username'),password=request.data.get('password'))
            refresh=RefreshToken.for_user(user)
            access=refresh.access_token
            return Response({
                'message':"login successful",
                'refresh':str(refresh),
                'access':str(access)
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist :
            return Response({'message':"invalid"},status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes=[AllowAny]
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            otp = OTP.objects.create(user=user, expires_at=timezone.now() + timezone.timedelta(minutes=5))
            print(otp.otp_code)
            # Send OTP via email/SMS (implement sending logic)
            return Response({"message": "OTP sent."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes=[AllowAny]
    def post(self, request):
        otp_code = request.data.get('otp_code')
        try:
            otp = OTP.objects.get(otp_code=otp_code)
            if otp.is_expired():
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
            reset_token = RefreshToken.for_user(otp.user)
            reset_token['scope'] = 'password_reset'
            return Response({
                'message': 'OTP verified successfully',
                'resetToken': str(reset_token.access_token) 
            }, status=status.HTTP_200_OK)
        except OTP.DoesNotExist:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

class NewPasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = NewPasswordSerializer
    permission_classes=[AllowAny]
    def post(self, request):
        reset_token = request.data.get('resetToken')
        new_password = request.data.get('newPassword')

        # Verify the JWT token and check the scope
        try:
            decoded_token = JWTAuthentication().get_validated_token(reset_token)

            # Check if the token's scope is 'password_reset'
            if decoded_token.get('scope') != 'password_reset':
                return Response({'error': 'Invalid token scope.'}, status=status.HTTP_403_FORBIDDEN)

            # Token is valid, reset the user's password
            user = User.objects.get(id=decoded_token['user_id'])
            user.password=new_password
            user.save()

            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)

        except InvalidToken:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

