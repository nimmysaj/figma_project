from django.shortcuts import render
from .serializers import *
from Accounts.models import ServiceProvider
from django.views import generic
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth.models import update_last_login
from django_filters.rest_framework import DjangoFilterBackend
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
        franchisee_id = self.request.query_params.get('franchisee_id')

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
        for f in Franchisee.objects.values('id', 'user__full_name')]
        return Response({
            "franchisee_profile": franchisee_profile,
                "franchisee_list": franchisee_dropdown,
                "service_providers": service_providers_data,
            })


# franchise login view
class FranchiseeLoginView(generics.GenericAPIView):
    serializer_class = FranchiseLoginSerializer


    def post(self, request, *args, **kwargs):
        serializer = FranchiseLoginSerializer(data=request.data)
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

def createserviceprovider(response):
    return HttpResponse("create servive provider")