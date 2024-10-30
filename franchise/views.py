from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status, permissions
from rest_framework import generics,viewsets
from service_provider.permissions import IsOwnerOrAdmin
from django.utils.encoding import smart_bytes, smart_str
from twilio.rest import Client
from rest_framework.decorators import action
from copy import deepcopy
from .serializers import *
from Accounts.models import *
from django.views import generic
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth.models import update_last_login
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.http import HttpResponse
from django.shortcuts import render

# list all service providers
class ServiceProviderListView(ListAPIView):
    serializer_class = ServiceProviderListSerializer
    queryset = ServiceProvider.objects.all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['user__full_name', 'user__district__name']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        franchisee_id = self.request.query_params.get('franchisee_id') # get service providers based on franchisee id for drop down menu

        # only return service providers under the logged in franchisee
        if franchisee_id:
            try:
                franchisee = Franchisee.objects.get(id=franchisee_id)
            except Franchisee.DoesNotExist:
                return ServiceProvider.objects.none()    
        else:
            try:
                franchisee = Franchisee.objects.get(user=user)
            except Franchisee.DoesNotExist:
                return ServiceProvider.objects.none()
                    
      
        # filter service providers for the franchisee    
        queryset = ServiceProvider.objects.filter(franchisee=franchisee)
        
        
        # sorting the list based on the parameter
        sort_order = self.request.query_params.get('sort', 'newest')

        if sort_order == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_order == 'newest':
            queryset = queryset.order_by('-created_at')
        return queryset
    
    def list(self, request, *args,**kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset is None:
            return Response("There are no Service Providers under the current Franchise.", status=200)

        # setting pagination for the list
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many= True)
        service_providers_data = self.get_paginated_response(serializer.data) if page else serializer.data

        # franchisee profile info
        franchisee = Franchisee.objects.get(user=request.user)
        franchisee_profile = {
            "name": franchisee.user.full_name,
            "image": franchisee.profile_image.url if franchisee.profile_image else None,
            "title": "Franchisee"
        }

        # frachisee dropdown list
        franchisee_dropdown = [{
            "id": f["id"],
            "name": f["user__full_name"]
        }
          for f in Franchisee.objects.values('id', 'user__full_name')
    ]

        return Response({
            "franchisee_profile": franchisee_profile,
            "franchisee_list": franchisee_dropdown,
            "service_providers": service_providers_data,
        }) 

# franchise login view
class FranchiseeLoginView(generics.GenericAPIView):
    serializer_class = FranchiseeLoginSerializer


    def post(self, request, *args, **kwargs):
        serializer = FranchiseeLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data['email_or_phone']
        password = serializer.validated_data['password']

        # Check if input is email or phone
        user = User.objects.filter(email=email_or_phone).first() or \
               User.objects.filter(phone_number=email_or_phone).first()

        if user and user.check_password(password):
            if user.is_franchisee:
                # Create JWT token
                refresh = RefreshToken.for_user(user)
                update_last_login(None, user)

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'User is not a franchisee.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        
# Set New Password
class SetNewPasswordView(generics.UpdateAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password has been updated successfully.'}, status=status.HTTP_200_OK)

# Forgot Password
class FranchiseePasswordForgotView(generics.GenericAPIView):
    serializer_class = FranchiseePasswordForgotSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data['email_or_phone']

        user = (User.objects.get(email=email_or_phone, is_franchisee=True) if '@' in email_or_phone 
                else User.objects.get(phone_number=email_or_phone, is_franchisee=True))

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(smart_bytes(user.pk))
        reset_link = f"http://127.0.0.1:8000/franchisee/password-reset/{uid}/{token}/"

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
            print(reset_link)
            return Response({'details': 'Password reset link has been sent to your phone.'}, status=status.HTTP_200_OK)

# Reset Password
class ResetPasswordView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'details': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
        return Response({'details': 'Invalid token or User ID'}, status=status.HTTP_400_BAD_REQUEST)

# Franchisee Profile Update
class FranchiseeViewSet(viewsets.ModelViewSet):
    permission_class = [permissions.IsAuthenticated]
    queryset = Franchisee.objects.all()
    serializer_class = FranchiseeSerializer

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Franchisee.objects.all()
        return Franchisee.objects.filter(user=self.request.user)

# Franchisee Registration and Update
class FranchiseeRegisterViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        try:
            franchisee = Franchisee.objects.get(user=request.user)
            queryset = FranchiseeRegister.objects.filter(franchisee=franchisee.id)

            if not queryset.exists():
                return Response({"message": "No services found for this franchisee."}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = FranchiseeRegisterSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"Error fetching services: {e}")
            return Response({"error": "An error occurred while retrieving services."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(FranchiseeRegister, pk=pk)
        serializer = FranchiseeRegisterSerializer(instance)
        return Response(serializer.data)
    
    def create(self, request):
        try:
            franchise = Franchisee.objects.get(user=request.user)

            existing_service = FranchiseeRegister.objects.filter(
                franchise=franchise,
                category=request.data.get('category'),
                subcategory=request.data.get('subcategory')
            ).exists()

            #if existing_service:
               # return Response({"message": "This service is already registered by the franchisee."}, status=status.HTTP_400_BAD_REQUEST)

            accepted_terms = request.data.get('accepted_terms', False)
            if not accepted_terms:
                return Response({"message": "You must accept the terms and conditions."}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = FranchiseeRegisterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(franchisee=franchise)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Franchisee.DoesNotExist:
            return Response({"error": "Franchisee not found for this user."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error during service registration: {str(e)}")
            return Response({"error": "An error occurred while registering the service.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        instance = get_object_or_404(FranchiseeRegister, pk=pk)
        accepted_terms = request.data.get('accepted_terms', False)
        if not accepted_terms:
            return Response({"message": "You must accept the terms and conditions."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FranchiseeRegisterUpdateSerializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            instance.save()
            return Response({
                "message": "Franchisee updated successfully.",
                "data": serializer.data,
                "available_lead_balance": instance.available_lead_balance,
                "added_lead": serializer.context.get('total_lead_quantity'),
                "amount_to_paid": serializer.context.get('amount_to_paid'),
            }, status=status.HTTP_200_OK)

        return Response({"message": "Failed to update .", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ServiceProviderListView(generics.ListAPIView):
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        # Get the franchise of the logged-in user
        franchise = get_object_or_404(franchise, user=self.request.user)
        # Filter service providers under the franchise
        return ServiceProvider.objects.filter(franchise=franchise)
