from rest_framework import generics, status
from rest_framework.response import Response
from .models import User, OTP
from .serializers import ForgotPasswordSerializer, VerifyOTPSerializer, NewPasswordSerializer
from django.utils import timezone
import random

class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            otp = OTP.objects.create(user=user, expires_at=timezone.now() + timezone.timedelta(minutes=5))
            # Send OTP via email/SMS (implement sending logic)
            return Response({"message": "OTP sent."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        otp_code = request.data.get('otp_code')
        try:
            otp = OTP.objects.get(otp_code=otp_code)
            if otp.is_expired():
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "OTP verified."}, status=status.HTTP_200_OK)
        except OTP.DoesNotExist:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

class NewPasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = NewPasswordSerializer

    def post(self, request):
        user_id = request.data.get('user_id')  # User ID should be sent to reset the password
        new_password = request.data.get('password')
        try:
            user = self.get_object(user_id)
            serializer = self.get_serializer(user, data={'password': new_password}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

