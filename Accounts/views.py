from django.shortcuts import render

# Create your views here.
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import ServiceProviderLoginSerializer, ServiceProviderPasswordResetSerializer, SetNewPasswordSerializer
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings



class ServiceProviderLoginView(generics.GenericAPIView):
    serializer_class = ServiceProviderLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh':str(refresh),
            'access':str(refresh.access_token),
        })
    
class ServiceProviderPasswordResetView(generics.GenericAPIView):
    serializer_class = ServiceProviderPasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # password reset link -
            reset_link = f"http://127.0.0.1:8000/api/accounts/service-provider/password-reset/{uid}/{token}/"

            # Here you can send the email
            send_mail(
                'Password Reset Required',
                f"You requested a password reset. Here is your Link: {reset_link}",
                settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )



            return Response({'details':'Password reset email sent for service provider.'})
        except User.DoesNotExist:
            return Response({'details': 'Email not registered.'}, status=status.HTTP_404_NOT_FOUND)
        
class ResetPasswordView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        
        if user is not None and default_token_generator.check_token(user, token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'details': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
        return Response({'details':'Invalid token or User ID'}, status=status.HTTP_400_BAD_REQUEST)
    


            
    
    