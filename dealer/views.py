from django.shortcuts import render
from Accounts.models import *  # Ensure you import your models
from rest_framework_simplejwt.authentication import JWTAuthentication


# Create your views here.

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import DealerLoginSerializer

# class DealerLoginView(generics.GenericAPIView):
#     serializer_class = DealerLoginSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']

#         # Generate a token for the authenticated user
#         token, created = Token.objects.get_or_create(user=user)

#         return Response({
#             'message': 'Login successful',
#             'token': token.key,  # Include the token in the response
#             'user_id': user.id,
#             'email': user.email,
#             'full_name': user.full_name,
#             'is_dealer': user.is_dealer,
#         }, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login


# Define the login view for dealers
class DealerLoginView(APIView):
    def post(self, request):
        serializer = DealerLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if user.is_dealer:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            update_last_login(None, user)  # Update last login timestamp

            return Response({
                'refresh': str(refresh),              # Refresh token
                'access': str(refresh.access_token),  # Access token
                'user_id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_dealer': user.is_dealer,
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'User is not a dealer.'}, status=status.HTTP_403_FORBIDDEN)

# from django.shortcuts import get_object_or_404
# from rest_framework import generics
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.permissions import IsAuthenticated
# from .serializers import ServiceProviderSerializer

# from django.shortcuts import get_object_or_404

# class DealerServiceProviderListView(generics.ListAPIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer_class = ServiceProviderSerializer

#     def get_queryset(self):
#         user = self.request.user  # This is a User instance
#         print(f"User: {user}, Type: {type(user)}, Is Dealer: {user.is_dealer}")  # Added Is Dealer check
#         dealer = get_object_or_404(Dealer, user=user)
#         print(f"Dealer: {dealer}, Type: {type(dealer)}")  # Print dealer details

#         return ServiceProvider.objects.filter(dealer=dealer)


from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter  # Add SearchFilter import
from Accounts.models import ServiceProvider, Dealer  # Ensure you import Dealer model
from .serializers import ServiceProviderSerializer

# class DealerServiceProviderListView(generics.ListAPIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer_class = ServiceProviderSerializer
#     filter_backends = [SearchFilter]  # Enable search functionality
#     search_fields = ['user__full_name', 'user__phone_number', 'user__district__name']  # Define search fields

#     def get_queryset(self):
#         user = self.request.user  # Get the logged-in user
#         dealer = get_object_or_404(Dealer, user=user)  # Ensure the user is a dealer
#         return ServiceProvider.objects.filter(dealer=dealer)  # Filter by dealer

# class DealerServiceProviderListView(generics.ListAPIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer_class = ServiceProviderSerializer
#     filter_backends = [SearchFilter]
#     search_fields = ['user__full_name', 'user__phone_number', 'user__district__name']

#     def get_queryset(self):
#         user = self.request.user
#         dealer = get_object_or_404(Dealer, user=user)
#         return ServiceProvider.objects.filter(dealer=dealer)

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         user = self.request.user
#         dealer = get_object_or_404(Dealer, user=user)
#         context['dealer'] = dealer  # Pass dealer to the context
#         return context



class DealerServiceProviderListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]  # Use JWT authentication here
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceProviderSerializer
    filter_backends = [SearchFilter]
    search_fields = ['user__full_name', 'user__phone_number', 'user__district__name']

    def get_queryset(self):
        user = self.request.user
        dealer = get_object_or_404(Dealer, user=user)
        return ServiceProvider.objects.filter(dealer=dealer)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        dealer = get_object_or_404(Dealer, user=user)
        context['dealer'] = dealer  # Pass dealer to the context
        return context
    

from rest_framework.views import APIView


# class DealerServiceProviderCountsView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         dealer = get_object_or_404(Dealer, user=user)
        
#         total_service_providers = ServiceProvider.objects.filter(dealer=dealer).count()
#         approved_count = ServiceProvider.objects.filter(dealer=dealer, verification_by_dealer='APPROVED').count()
#         pending_count = ServiceProvider.objects.filter(dealer=dealer, verification_by_dealer='PENDING').count()

#         data = {
#             "total_service_providers": total_service_providers,
#             "approved_count": approved_count,
#             "pending_count": pending_count,
#         }
#         return Response(data)


class DealerServiceProviderCountsView(APIView):
    authentication_classes = [JWTAuthentication]  # Use JWT for access and refresh tokens
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        dealer = get_object_or_404(Dealer, user=user)
        
        total_service_providers = ServiceProvider.objects.filter(dealer=dealer).count()
        approved_count = ServiceProvider.objects.filter(dealer=dealer, verification_by_dealer='APPROVED').count()
        pending_count = ServiceProvider.objects.filter(dealer=dealer, verification_by_dealer='PENDING').count()

        data = {
            "total_service_providers": total_service_providers,
            "approved_count": approved_count,
            "pending_count": pending_count,
        }
        return Response(data)


# class DealerServiceProviderPendingListView(generics.ListAPIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer_class = ServiceProviderSerializer
#     filter_backends = [SearchFilter]
#     search_fields = ['user__full_name', 'user__phone_number', 'user__district__name']

#     def get_queryset(self):
#         user = self.request.user  # Ensure this is within the correct method
#         dealer = get_object_or_404(Dealer, user=user)
#         return ServiceProvider.objects.filter(dealer=dealer, verification_by_dealer='PENDING')

from .serializers import *

class DealerServiceProviderPendingListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]  # Use JWT for access and refresh tokens
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceProviderPendingSerializer
    filter_backends = [SearchFilter]
    search_fields = ['user__full_name', 'user__phone_number', 'user__district__name']

    def get_queryset(self):
        user = self.request.user
        dealer = get_object_or_404(Dealer, user=user)
        return ServiceProvider.objects.filter(dealer=dealer, verification_by_dealer='PENDING')


from .serializers import ServiceProviderPendingSerializer

# class UpdateServiceProviderStatusView(generics.UpdateAPIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer_class = ServiceProviderPendingSerializer

#     def get_object(self):
#         # Retrieve the service provider by ID from the URL
#         service_provider_id = self.kwargs.get('id')  # Assuming the URL includes an ID
#         user = self.request.user  # Get the logged-in user
#         dealer = get_object_or_404(Dealer, user=user)  # Ensure the user is a dealer
        
#         # Get the service provider and ensure it belongs to the logged-in dealer
#         service_provider = get_object_or_404(ServiceProvider, id=service_provider_id, dealer=dealer)
#         return service_provider

#     def perform_update(self, serializer):
#         # Change the status to 'APPROVED'
#         serializer.instance.verification_by_dealer = 'APPROVED'
#         serializer.save()


class UpdateServiceProviderStatusView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]  # Use JWT for access and refresh tokens
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceProviderPendingSerializer

    def get_object(self):
        # Retrieve the service provider by ID from the URL
        service_provider_id = self.kwargs.get('id')  # Assuming the URL includes an ID
        user = self.request.user  # Get the logged-in user
        dealer = get_object_or_404(Dealer, user=user)  # Ensure the user is a dealer
        
        # Get the service provider and ensure it belongs to the logged-in dealer
        service_provider = get_object_or_404(ServiceProvider, id=service_provider_id, dealer=dealer)
        return service_provider

    def perform_update(self, serializer):
        # Change the status to 'APPROVED'
        serializer.instance.verification_by_dealer = 'APPROVED'
        serializer.save()


from .serializers import FranchiseSerializer

class DealerFranchiseeDetailView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Ensure the user is a dealer
        if not request.user.is_dealer:
            return Response({
                'message': 'Access denied. User is not a dealer.'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            # Retrieve the dealer object for the logged-in user
            dealer = Dealer.objects.get(user=request.user)

            # Retrieve the franchisee data associated with this dealer
            franchisee = dealer.franchisee
            franchisee_data = FranchiseSerializer(franchisee).data

            return Response({
                'message': 'Franchisee data retrieved successfully',
                'franchisee_data': franchisee_data
            }, status=status.HTTP_200_OK)

        except Dealer.DoesNotExist:
            return Response({
                'message': 'Dealer profile not found for this user.'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'message': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# from rest_framework import generics
# from rest_framework.filters import SearchFilter  # Correct import for SearchFilter
# from .serializers import ServiceproviderSerializerSearch
# from .serializers import *

# class SearchAPIView(generics.ListCreateAPIView):
#     search_fields = ['user__full_name', 'user__phone_number', 'user__district__name']  # Correct fields
#     filter_backends = (SearchFilter,)  # Use SearchFilter directly
#     queryset = ServiceProvider.objects.all()
#     serializer_class = ServiceproviderSerializerSearch




# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from Accounts.models import Dealer
from .serializers import DealerFranchiseeSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def franchise_details_view(request):
    try:
        # Check if the user is a dealer and retrieve the dealer object
        dealer = Dealer.objects.get(user=request.user)
        
        # Retrieve the franchise associated with the dealer
        franchise = dealer.franchisee

        # Serialize the franchise data
        serializer = DealerFranchiseeSerializer(franchise)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Dealer.DoesNotExist:
        return Response(
            {"error": "Dealer profile not found."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except AttributeError:
        return Response(
            {"error": "No franchise associated with this dealer."},
            status=status.HTTP_400_BAD_REQUEST
        )




# class DealerServiceProviderDetailView(APIView):
#     authentication_classes = [JWTAuthentication]  # Use JWT for access and refresh tokens
#     permission_classes = [IsAuthenticated]

#     def get(self, request, service_provider_id):
#         user = request.user
#         dealer = get_object_or_404(Dealer, user=user)

#         service_provider = get_object_or_404(ServiceProvider, id=service_provider_id, dealer=dealer)

#         service_provider_data = ServiceProviderSerializer(service_provider)

#         services = service_provider.services.all()  # Get all services registered by the service provider

#         services_data = ServiceSerializer(services, many=True).data

#         response_data = {
#             'service_provider': service_provider_data.data,
#             'services': services_data,
#         }
#         return Response(response_data, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from rest_framework import status

class DealerServiceProviderDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, service_provider_id):
        try:
            # Get the dealer based on authenticated user
            user = request.user
            dealer = get_object_or_404(Dealer, user=user)

            # Get the service provider and verify they belong to this dealer
            service_provider = get_object_or_404(
                ServiceProvider, 
                id=service_provider_id, 
                dealer=dealer
            )

            # Get service provider details
            service_provider_data = ServiceProviderSerializer(service_provider).data

            # Get all services registered by the service provider
            services = service_provider.services.all()
            services_data = []
            
            for service in services:
                service_data = ServiceSerializer(service).data
                
                # Get ads related to this service
                ads = Ads.objects.filter(
                    service=service,
                    service_provider=service_provider
                )
                ads_data = AdsSerializer(ads, many=True).data
                
                # Combine service and its ads data
                service_data['ads'] = ads_data
                services_data.append(service_data)

            # Get all ads for this service provider
            all_ads = Ads.objects.filter(service_provider=service_provider)
            all_ads_data = AdsSerializer(all_ads, many=True).data

            response_data = {
                'service_provider': service_provider_data,
                'services': services_data,
                'all_ads': all_ads_data,  # All ads regardless of service
                'total_services': len(services_data),
                'total_ads': len(all_ads_data),
                'status': 'success'
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ServiceProvider.DoesNotExist:
            return Response(
                {'error': 'Service provider not found or not associated with this dealer'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


from Accounts.models import Dealer, PaymentRequest

    
class PaymentRequestCreateView(APIView):
    def post(self, request, *args, **kwargs):
        dealer = Dealer.objects.filter(user=request.user).first()  # Adjust to fetch the dealer instance based on the logged-in user

        if dealer is None:
            return Response({"error": "No dealer instance found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch the receiver, assuming you want a superuser or any user
        receiver = User.objects.filter(is_superuser=True).first()  # Change as necessary
        # Alternatively, if you want any user:
        # receiver = User.objects.first()

        if receiver is None:
            return Response({"error": "No superuser found to set as receiver."}, status=status.HTTP_404_NOT_FOUND)

        # Extract data from request
        data = request.data
        # Ensure all required fields are present
        required_fields = [
            "amount", "description", "phone", "payment_method",
            "account_holder_name", "bank_name", "bank_branch",
            "account_number", "ifsc_code", "email"
        ]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return Response(
                {field: "This field is required." for field in missing_fields},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the payment request
        try:
            payment_request = PaymentRequest.objects.create(
                sernder=dealer,  # Valid dealer instance
                receiver=receiver,
                amount=data["amount"],
                description=data["description"],
                email=data["email"],
                country_code=data.get("country_code"),  # Adjust if necessary
                phone=data["phone"],
                payment_method=data["payment_method"],
                account_holder_name=data["account_holder_name"],
                bank_name=data["bank_name"],
                bank_branch=data["bank_branch"],
                account_number=data["account_number"],
                ifsc_code=data["ifsc_code"],
            )
            serializer = PaymentRequestSerializer(payment_request)  # Assuming you have a serializer
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)