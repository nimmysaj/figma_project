# accounts/views.py

from rest_framework import generics, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.response import Response
from .models import User, OTP
from .serializers import ForgotPasswordSerializer, VerifyOTPSerializer, NewPasswordSerializer
from django.utils import timezone
import random

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

            
