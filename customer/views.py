from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, OTP
from .serializers import UserRegistrationSerializer, OTPVerifySerializer

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Save user and retrieve the user object
            return Response({'message': 'User registered successfully. OTP sent to the provided contact method.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def post(self, request, *args, **kwargs):
        # Only pass the OTP code to the serializer
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            # Optionally delete OTP after successful verification
            otp_code = request.data.get('otp_code')
            otp_instance = OTP.objects.filter(otp_code=otp_code).latest('created_at')
            otp_instance.delete()  # Delete or mark as used
            return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

