from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics,viewsets
from Accounts.models import ServiceProvider, User
from .serializers import ServiceProviderPasswordForgotSerializer, SetNewPasswordSerializer, ServiceProviderLoginSerializer,ServiceProviderSerializer
from django.utils.encoding import smart_bytes, smart_str
from twilio.rest import Client
# Create your views here.
class ServiceProviderLoginView(APIView):
    def post(self, request):
        serializer = ServiceProviderLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data['email_or_phone']
        password = serializer.validated_data['password']

        # Check if input is email or phone
        user = User.objects.filter(email=email_or_phone).first() or \
               User.objects.filter(phone_number=email_or_phone).first()

        if user and user.check_password(password):
            if user.is_service_provider:
                # Create JWT token
                refresh = RefreshToken.for_user(user)
                update_last_login(None, user)  # Update last login time

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'User is not a service provider.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordView(generics.UpdateAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request, *args, **kwargs):
        user = request.user  # Get the authenticated user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set the new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'detail': 'Password has been updated successfully.'}, status=status.HTTP_200_OK)


class ServiceProviderPasswordForgotView(generics.GenericAPIView):
    serializer_class = ServiceProviderPasswordForgotSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Validate the input (email or phone)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data['email_or_phone']

        # Determine if it's an email or phone and find the user
        if '@' in email_or_phone:
            user = User.objects.get(email=email_or_phone, is_service_provider=True)
        else:
            user = User.objects.get(phone_number=email_or_phone, is_service_provider=True)

        # Generate the password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(smart_bytes(user.pk))

        # Generate the reset link
        reset_link = f"http://127.0.0.1:8000/service-provider/password-reset/{uid}/{token}/"

        # Send an email if an email was provided
        if '@' in email_or_phone:
            send_mail(
                'Password Reset Request',
                f"Use the following link to reset your password: {reset_link}",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return Response({'details': 'Password reset link has been sent to your email.'}, status=status.HTTP_200_OK)
        else:
            # For testing purposes, we are not sending an SMS yet, but this is where SMS logic would go
            # For example, you would use Twilio to send the SMS:
        #     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        #     message = client.messages.create(
        #     from_=settings.TWILIO_PHONE_NUMBER,
        #     body=f"{reset_link}",
        #     to=user.phone_number,
        #     )
        #     print(message.sid)
            return Response({'details': 'Password reset link has been sent to your phone.'}, status=status.HTTP_200_OK)


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'details': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
        return Response({'details': 'Invalid token or User ID'}, status=status.HTTP_400_BAD_REQUEST)
    

class ServiceProviderViewSet(viewsets.ModelViewSet):
    permission_class =[IsAuthenticated]
    queryset =ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    
