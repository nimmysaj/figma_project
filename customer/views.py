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
from Accounts.models import User, OTP
from .serializers import ForgotPasswordSerializer, VerifyOTPSerializer, NewPasswordSerializer,LoginSerializer
from django.utils import timezone


# Create your views here.

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

