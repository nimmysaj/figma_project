from django.shortcuts import render
<<<<<<< HEAD

# Create your views here.
from Accounts.models import ServiceProviderVerification
from .serializers import ServiceProviderVerificationSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import DealerLoginSerializer

=======
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from Accounts.models import ServiceProvider,User,Dealer
from django.db.models import Q
from rest_framework import serializers
from rest_framework import generics
from .serializers import DealerLoginSerializer
from service_provider.permissions import IsOwnerOrAdmin
# Create your views here.

# Dealer Login
>>>>>>> f568851c93265555359d959eef8979965dcd140b
class DealerLoginView(generics.GenericAPIView):
    serializer_class = DealerLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate a token for the authenticated user
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'message': 'Login successful',
            'token': token.key,  # Include the token in the response
            'user_id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'is_dealer': user.is_dealer,
        }, status=status.HTTP_200_OK)

<<<<<<< HEAD
# List and Create View
class ServiceProviderVerificationListCreate(generics.ListCreateAPIView):
    queryset = ServiceProviderVerification.objects.all()
    serializer_class = ServiceProviderVerificationSerializer

# Retrieve, Update, Delete View
class ServiceProviderVerificationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceProviderVerification.objects.all()
    serializer_class = ServiceProviderVerificationSerializer
=======
# Combining the two list and return as serializer response
class CombinedDetailsSerializer(serializers.Serializer):
    provider_details = serializers.ListField(child = serializers.DictField())
    additional_details = serializers.ListField(child = serializers.DictField())

class ServiceProviderView(APIView):
    permission_class =[IsAuthenticated, IsOwnerOrAdmin]

    def get(self, request,*args, **kwargs):
        try:
           
            dealer = Dealer.objects.get(user_id=request.user.id)
            # Find the ServiceProviders for the authenticated user (dealer)
            query = Q(dealer_id=dealer.id) & Q(verification_by_dealer = "APPROVED")
            queryset = ServiceProvider.objects.filter(query) 
            
            if not queryset.exists():
                return Response(
                    {"message": "No service providers are added."},
                        status=status.HTTP_404_NOT_FOUND
                )

            # Taken the total_providers,total verified providers,total pending request 
            total_providers = ServiceProvider.objects.filter(dealer_id=dealer.id).count()
            verified_providers = ServiceProvider.objects.filter(Q(query) & Q(verification_by_dealer = "APPROVED")).count()
            pending_providers = ServiceProvider.objects.filter(Q(query) & Q(verification_by_dealer = "PENDING")).count()
            additional_details = []
            additional_details = [
                    {'total_providers': total_providers,
                    'total_verified': verified_providers,
                    'total_pending' : pending_providers
                    }
            ]

            # Taken the details of the service provider
            provider_details = []
            for service_provider in queryset:
                service_provider_details = User.objects.get(id=service_provider.user.id)
                service_provider_profile = ServiceProvider.objects.get(id = service_provider.id)
                provider_details.append({
                        'name':service_provider_details.full_name,
                        'custom_id': service_provider_profile.custom_id,
                        'dob':service_provider_profile.date_of_birth,
                        'verifiedby':service_provider_profile.dealer.user.full_name,
                        'location':service_provider_details.district.name,
                        'contact':service_provider_details.phone_number,
                        'email':service_provider_details.email,
                        'status':service_provider_profile.status,
                })
            serializer = CombinedDetailsSerializer({
                    'additional_details':additional_details,
                    'provider_details':provider_details
            })
                
            return Response(serializer.data, status=200)

        except Exception as e:
            # Log the error for debugging
            print(f"Error fetching service providers: {e}")
            return Response(
                {"error": "An error occurred while retrieving service providers."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ProviderSearchView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access

    def get(self,request):
        try:
            dealer = Dealer.objects.get(user_id=request.user.id)
            query = request.query_params.get('search',None)
            if not query:
                return Response(
                        {"message": "Please provide provider name in search bar."},
                        status=status.HTTP_404_NOT_FOUND
                )
            else:
                providers_list = User.objects.filter(Q(full_name__icontains = query) | Q(district__name__icontains = query)) 
                if providers_list.exists():
                    service_providers = []
                    for rec in providers_list:
                        try:
                            providers_details = ServiceProvider.objects.get(Q(user_id= rec.id) & Q(dealer_id = dealer.id) & Q(verification_by_dealer = "APPROVED"))
                            user_details = User.objects.get(id = rec.id) 
                            service_providers.append({
                                    'name':user_details.full_name,
                                    'custom_id': providers_details.custom_id,
                                    'dob':providers_details.date_of_birth,
                                    'verifiedby':providers_details.dealer.user.full_name,
                                    'location':user_details.district.name,
                                    'contact':user_details.phone_number,
                                    'email':user_details.email,
                                    'status':providers_details.status,
                            }) 
                        except ServiceProvider.DoesNotExist:
                            return Response({"message": "No service providers are added."})
                   
                    return Response(service_providers,status=200)
                else:
                    return Response(
                    {"message": "No service providers are added."},
                        status=status.HTTP_404_NOT_FOUND
                    )
        except Exception as e:
            # Log the error for debugging
            print(f"Error fetching service providers: {e}")
            return Response(
                {"error": "An error occurred while retrieving service providers."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )        


>>>>>>> f568851c93265555359d959eef8979965dcd140b
