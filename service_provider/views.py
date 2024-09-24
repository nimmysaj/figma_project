from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ServiceProviderRegistrationSerializer, OTPVerificationSerializer

class ServiceProviderRegistrationView(APIView):
    def post(self, request):
        serializer = ServiceProviderRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "OTP sent to email"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.verify_otp()
            return Response({"detail": "OTP verified, user activated."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
