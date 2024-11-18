from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from Accounts.models import ServiceProvider,User,Dealer
from django.db.models import Q
from rest_framework import serializers
from rest_framework import generics
from .serializers import LoginSerializer
from rest_framework.pagination import PageNumberPagination


# Create your views here.

# Common Login function for Customer,Service Provider,Dealer and Franchisee

class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny] 
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate a token for the authenticated user
        token, created = Token.objects.get_or_create(user=user)
        
        user_type = None
        if user.is_customer:
            user_type = "Customer"
        elif user.is_service_provider:
            user_type = "Service-Provider"
        elif user.is_dealer:
            user_type = "Dealer"
        elif user.is_franchisee:
            user_type = "Franchisee"  
        elif user.is_superuser:
            user_type = "Superuser" 
        elif user.is_staff:
            user_type = "Staff"    

        return Response({
            'message': 'Login successful',
            'token': token.key,  # Include the token in the response
            'user_id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'user_type': user_type,
        }, status=status.HTTP_200_OK)

# Custom Pagination
class CustomPagination(PageNumberPagination):
    page_size = 6 #Default number of dealers per page
    page_size_query_param = 'page_size' #Allow users to specify page size
    max_page_size = 6

# Combining the two list and return as serializer response
class CombinedDetailsSerializer(serializers.Serializer):
    provider_details = serializers.ListField(child = serializers.DictField())
    additional_details = serializers.ListField(child = serializers.DictField())

class ServiceProviderListView(APIView):
    permission_class =[IsAuthenticated]

    def get(self, request,*args, **kwargs):
        try:
           
            dealer = Dealer.objects.get(user_id=request.user.id)
            # Find the ServiceProviders for the authenticated user (dealer)
            query = Q(dealer_id=dealer.id) & Q(verification_by_dealer = "APPROVED")
            queryset = ServiceProvider.objects.filter(query).order_by('id') 
            
            if not queryset.exists():
                return Response(
                    {"message": "No service providers are added."},
                        status=status.HTTP_404_NOT_FOUND
                )

            # Taken the total_providers,total verified providers,total pending request 
            total_providers = ServiceProvider.objects.filter(dealer_id=dealer.id).count()
            verified_providers = ServiceProvider.objects.filter(query).count()
            pending_providers = ServiceProvider.objects.filter(Q(dealer_id=dealer.id) & Q(verification_by_dealer = "PENDING")).count()
            additional_details = []
            additional_details = [
                    {'total_providers': total_providers,
                    'total_verified': verified_providers,
                    'total_pending' : pending_providers
                    }
            ]

            # Taken the details of the service provider
            paginator = CustomPagination()
            paginated_dealers = paginator.paginate_queryset(queryset, request)
            provider_details = []
            for service_provider in paginated_dealers:
                service_provider_details = User.objects.get(id=service_provider.user.id)
                service_provider_profile = ServiceProvider.objects.get(id = service_provider.id)
                provider_details.append({
                        'name':service_provider_details.full_name,
                        'custom_id': service_provider_profile.custom_id,
                        'dob':service_provider_profile.date_of_birth,
                        'verifiedby':service_provider_profile.dealer.user.full_name,
                        'location': service_provider_details.district.name if service_provider_details.district else 'Unknown Location',
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
                providers_list = User.objects.filter(Q(full_name__icontains = query) | Q(district__name__icontains = query)).order_by('id')
                paginator = CustomPagination()
                paginated_dealers = paginator.paginate_queryset(providers_list, request)  
                service_providers = []
                for rec in paginated_dealers:
                    try:
                        providers_details = ServiceProvider.objects.get(Q(user_id= rec.id) & Q(dealer_id = dealer.id) & Q(verification_by_dealer = "APPROVED"))
                        provider_user = User.objects.get(id = rec.id) 
                        service_providers.append({
                                'name':provider_user.full_name,
                                'custom_id': providers_details.custom_id,
                                'dob':providers_details.date_of_birth,
                                'verifiedby':providers_details.dealer.user.full_name,
                                'location': provider_user.district.name if provider_user.district else 'Unknown Location',
                                'contact':provider_user.phone_number,
                                'email':provider_user.email,
                                'status':providers_details.status,
                        }) 
                    except ServiceProvider.DoesNotExist:
                        return Response({"message": "No service providers are added."})
                   
                return Response(service_providers,status=200)
                
        except Exception as e:
            # Log the error for debugging
            print(f"Error fetching service providers: {e}")
            return Response(
                {"error": "An error occurred while retrieving service providers."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )        

class ProviderSortView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access

    def get(self,request):
        try:
            dealer = Dealer.objects.get(user_id=request.user.id)
            query = request.query_params.get('search',None)
            sort_by = request.query_params.get('sort_by',None) # sort_by = id(Ascending) ,sort_by = -id(Descending)
            paginator = CustomPagination()
            service_providers = []
            if query:
                providers_list = User.objects.filter(Q(full_name__icontains = query) | Q(district__name__icontains = query)).order_by(sort_by) 
                paginator = CustomPagination()
                paginated_dealers = paginator.paginate_queryset(providers_list, request)  
                for rec in paginated_dealers:
                    try:
                        providers_details = ServiceProvider.objects.get(Q(user_id= rec.id) & Q(dealer_id = dealer.id) & Q(verification_by_dealer = "APPROVED"))
                        provider_user = User.objects.get(id = rec.id) 
                        service_providers.append({
                                'name':provider_user.full_name,
                                'custom_id': providers_details.custom_id,
                                'dob':providers_details.date_of_birth,
                                'verifiedby':providers_details.dealer.user.full_name,
                                'location': provider_user.district.name if provider_user.district else 'Unknown Location',
                                'contact':provider_user.phone_number,
                                'email':provider_user.email,
                                'status':providers_details.status,
                        }) 
                    except ServiceProvider.DoesNotExist:
                        return Response({"message": "No service providers are added."})
            else:
                service_providers_list = ServiceProvider.objects.filter(Q(dealer_id=dealer.id) & Q(verification_by_dealer = "APPROVED")).order_by(sort_by) 
                paginator = CustomPagination()
                paginated_dealers = paginator.paginate_queryset(service_providers_list, request) 
                for service_provider in paginated_dealers:
                    service_provider_details = User.objects.get(id=service_provider.user.id)
                    service_provider_profile = ServiceProvider.objects.get(id = service_provider.id)
                    service_providers.append({
                            'name':service_provider_details.full_name,
                            'custom_id': service_provider_profile.custom_id,
                            'dob':service_provider_profile.date_of_birth,
                            'verifiedby':service_provider_profile.dealer.user.full_name,
                            'location': service_provider_details.district.name if service_provider_details.district else 'Unknown Location',
                            'contact':service_provider_details.phone_number,
                            'email':service_provider_details.email,
                            'status':service_provider_profile.status,
                    })
                    
            return Response(service_providers,status=200) 
        except Exception as e:
            # Log the error for debugging
            print(f"Error fetching service providers: {e}")
            return Response(
                {"error": "An error occurred while retrieving service providers."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )     