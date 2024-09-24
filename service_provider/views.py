from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from Accounts.models import User, OTP
from django.utils import timezone
from django.core.validators import validate_email
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
import random
from .serializers import RegisterSerializer, OTPVerificationSerializer

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # This will handle user creation and validation
            print(f'User created: {user}')  # Debug output
            
            # Create OTP instance
            otp = OTP.objects.create(user=user)
            
            # Send OTP via email
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp.otp_code}. It is valid for 5 minutes.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return Response({'message': 'User registered successfully. Please verify your email for OTP.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.verify_otp()
            return Response({"detail": "OTP verified, user activated."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)