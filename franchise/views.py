from django.shortcuts import render

# Create your views here.

# views.py
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import FranchiseeLoginSerializer

# class FranchiseeLoginView(generics.GenericAPIView):
#     serializer_class = FranchiseeLoginSerializer

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
#             'is_franchisee': user.is_franchisee,
#         }, status=status.HTTP_200_OK)

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .serializers import FranchiseeLoginSerializer

class FranchiseeLoginView(generics.GenericAPIView):
    serializer_class = FranchiseeLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Login successful',
            'refresh': str(refresh),
            'access': str(refresh.access_token),  # Include both tokens in the response
            'user_id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'is_franchisee': user.is_franchisee,
        }, status=status.HTTP_200_OK)


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from Accounts.models import *
from .serializers import ServiceProviderSerializer
from rest_framework import filters  # Import filters here

# class FranchiseeServiceProviderListView(generics.ListAPIView):
#     authentication_classes = [JWTAuthentication]  # Use JWT authentication
#     permission_classes = [IsAuthenticated]
#     serializer_class = ServiceProviderSerializer
#     filter_backends = [filters.SearchFilter]  # Use the filters module for SearchFilter
#     search_fields = ['user__full_name', 'user__phone_number', 'user__district__name']

#     def get_queryset(self):
#         user = self.request.user
#         # Get the Franchisee associated with the logged-in user
#         franchisee = get_object_or_404(Franchisee, user=user)
#         # Return the service providers associated with the franchisee
#         return ServiceProvider.objects.filter(franchisee=franchisee)

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         user = self.request.user
#         franchisee = get_object_or_404(Franchisee, user=user)
#         context['franchisee'] = franchisee  # Pass franchisee to the context
#         return context


class FranchiseeServiceProviderListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]  # Use JWT authentication
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceProviderSerializer
    filter_backends = [filters.SearchFilter]  # Use the filters module for SearchFilter
    search_fields = ['user__full_name', 'user__phone_number', 'user__district__name']

    def get_queryset(self):
        user = self.request.user
        # Get the Franchisee associated with the logged-in user
        franchisee = get_object_or_404(Franchisee, user=user)

        # Retrieve service providers associated with the franchisee
        queryset = ServiceProvider.objects.filter(franchisee=franchisee)

        # Handle sorting based on query parameters
        sort_option = self.request.query_params.get('sort', 'newest')  # Default to newest
        if sort_option == 'oldest':
            queryset = queryset.order_by('created_date')  # Sort by created_date ascending
        else:  # Default to 'newest'
            queryset = queryset.order_by('-created_date')  # Sort by created_date descending

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        franchisee = get_object_or_404(Franchisee, user=user)
        context['franchisee'] = franchisee  # Pass franchisee to the context
        return context


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class FranchiseeServiceProviderCountsView(APIView):
    authentication_classes = [JWTAuthentication]  # Use JWT for access and refresh tokens
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Get the Franchisee associated with the logged-in user
        franchisee = get_object_or_404(Franchisee, user=user)
        
        # Count service providers associated with the franchisee
        total_service_providers = ServiceProvider.objects.filter(franchisee=franchisee).count()
        approved_count = ServiceProvider.objects.filter(franchisee=franchisee, verification_by_dealer='APPROVED').count()
        pending_count = ServiceProvider.objects.filter(franchisee=franchisee, verification_by_dealer='PENDING').count()

        data = {
            "total_service_providers": total_service_providers,
            "approved_count": approved_count,
            "pending_count": pending_count,
        }
        return Response(data)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from Accounts.models import ServiceProvider, Franchisee, ServiceRegister, CustomerReview,ServiceRequest,Ads
from .serializers import *

# class FranchiseeServiceProviderDetailView(APIView):
#     authentication_classes = [JWTAuthentication]  # Use JWT for access and refresh tokens
#     permission_classes = [IsAuthenticated]

#     def get(self, request, service_provider_id):
#         user = request.user
#         franchisee = get_object_or_404(Franchisee, user=user)

#         service_provider = get_object_or_404(ServiceProvider, id=service_provider_id, franchisee=franchisee)

#         service_provider_data = ServiceProviderSerializer(service_provider)

#         services = service_provider.services.all()  # Get all services registered by the service provider
#         # reviews = service_provider.reviews.all()   

#         services_data = ServiceSerializer(services, many=True).data
#         # reviews_data = ReviewSerializer(reviews, many=True).data

#         response_data = {
#             'service_provider': service_provider_data.data,
#             'services': services_data,
#             # 'reviews': reviews_data,
#         }
#         return Response(response_data, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import Avg


class FranchiseeServiceProviderDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, service_provider_id):
        # Verify the franchisee making the request
        user = request.user
        franchisee = get_object_or_404(Franchisee, user=user)

        # Get the service provider and verify they belong to this franchisee
        service_provider = get_object_or_404(
            ServiceProvider, 
            id=service_provider_id, 
            franchisee=franchisee
        )

        # Get the service provider's user object for related data
        provider_user = service_provider.user

        # Get all related data
        services = ServiceRegister.objects.filter(service_provider=service_provider)
        customer_reviews = CustomerReview.objects.filter(service_provider=provider_user)
        service_requests = ServiceRequest.objects.filter(service_provider=provider_user)
        ads = Ads.objects.filter(service_provider=service_provider)

        # Serialize all the data
        response_data = {
            'service_provider': {
                'personal_info': {
                    'id': service_provider.id,
                    'custom_id': service_provider.custom_id,
                    'full_name': provider_user.full_name,
                    'email': provider_user.email,
                    'phone_number': provider_user.phone_number,
                    'profile_image': request.build_absolute_uri(service_provider.profile_image.url) if service_provider.profile_image else None,
                    'date_of_birth': service_provider.date_of_birth,
                    'gender': service_provider.gender,
                    'about': service_provider.about,
                },
                'business_info': {
                    'dealer': service_provider.dealer.custom_id,
                    'franchisee': service_provider.franchisee.custom_id,
                    'address_proof_document': service_provider.address_proof_document,
                    'id_number': service_provider.id_number,
                    'payout_required': service_provider.payout_required,
                    'status': service_provider.status,
                    'verification_by_dealer': service_provider.verification_by_dealer,
                    'created_date': service_provider.created_date,
                }
            },
            'services': [{
                'id': service.id,
                'description': service.description,
                'gstcode': service.gstcode,
                'category': service.category.title,
                'subcategory': service.subcategory.title,
                'status': service.status,
                'available_lead_balance': service.available_lead_balance,
                'image': request.build_absolute_uri(service.image.url) if service.image else None,
                'license': request.build_absolute_uri(service.license.url) if service.license else None,
            } for service in services],
            'customer_reviews': [{
                'id': review.id,
                'customer_name': review.customer.full_name,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at,
                'image': request.build_absolute_uri(review.image.url) if review.image else None,
            } for review in customer_reviews],
            'service_requests': [{
                'booking_id': str(request.booking_id),
                'title': request.title,
                'customer_name': request.customer.full_name,
                'service_title': request.service.subcategory.title,
                'work_status': request.work_status,
                'acceptance_status': request.acceptance_status,
                'request_date': request.request_date,
                'availability_from': request.availability_from,
                'availability_to': request.availability_to,
                'additional_notes': request.additional_notes,
                'image': request.build_absolute_uri(request.image.url) if request.image else None,
            } for request in service_requests],
            'ads': [{
                'id': ad.id,
                'title': ad.title,
                'ad_type': ad.ad_type,
                'service_title': ad.service.subcategory.title,
                'amount': str(ad.amount),
                'starting_date': ad.starting_date,
                'ending_date': ad.ending_date,
                'payment': ad.payment,
                'status': ad.status,
                'created': ad.created,
            } for ad in ads],
        }

        # Add summary statistics
        response_data['summary'] = {
            'total_services': services.count(),
            'total_reviews': customer_reviews.count(),
            'average_rating': customer_reviews.aggregate(Avg('rating'))['rating__avg'] or 0,
            'total_service_requests': service_requests.count(),
            'pending_requests': service_requests.filter(work_status='pending').count(),
            'active_ads': ads.filter(status='active').count(),
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response(
                {'error': 'Service provider not found or not associated with this franchisee'},
                status=status.HTTP_404_NOT_FOUND
            )
        return super().handle_exception(exc)


# class FranchiseeServiceProviderDetailView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, service_provider_id):
#         user = request.user
#         franchisee = get_object_or_404(Franchisee, user=user)

#         # Retrieve the service provider associated with the franchisee
#         service_provider = get_object_or_404(ServiceProvider, id=service_provider_id, franchisee=franchisee)

#         # Serialize service provider data
#         service_provider_data = ServiceProviderSerializer(service_provider)

#         # Get services registered by the service provider
#         services = service_provider.services.all()
#         services_data = ServiceSerializer(services, many=True).data

#         # Get recent service requests
#         service_requests = ServiceRequest.objects.filter(service_provider=service_provider).order_by('-request_date')[:5]
#         service_requests_data = ServiceRequestSerializer(service_requests, many=True).data

#         # Get ads associated with the service provider
#         ads = Ads.objects.filter(service_provider=service_provider).order_by('-created')[:5]
#         ads_data = AdsSerializer(ads, many=True).data

#         # Compile the response data
#         response_data = {
#             'service_provider': service_provider_data.data,
#             'services': services_data,
#             'recent_service_requests': service_requests_data,
#             'ads': ads_data,
#         }

#         return Response(response_data, status=status.HTTP_200_OK)


from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from Accounts.models import Franchisee, Dealer
from .serializers import DealerSerializer  # Create this serializer if it doesn't already exist

class FranchiseeDealerListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DealerSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__full_name', 'user__phone_number', 'user__district__name']

    def get_queryset(self):
        # Get the logged-in user
        user = self.request.user
        # Retrieve the Franchisee associated with the logged-in user
        franchisee = get_object_or_404(Franchisee, user=user)
        
        # Retrieve sorting option from URL path; default to 'newest' if not specified
        sort_option = self.kwargs.get('sort_option', 'newest')

        # Apply sorting order based on the path parameter
        queryset = Dealer.objects.filter(franchisee=franchisee)
        
        # Check sort option and apply ordering accordingly
        if sort_option == 'oldest':
            queryset = queryset.order_by('craeted_date')
        else:  # Default to 'newest'
            queryset = queryset.order_by('-craeted_date')

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['franchisee'] = get_object_or_404(Franchisee, user=self.request.user)
        return context
    

class FranchiseeDealerDetailView(APIView):
    authentication_classes = [JWTAuthentication]  # Use JWT authentication
    permission_classes = [IsAuthenticated]

    def get(self, request, dealer_id):
        # Get the logged-in user
        user = request.user
        # Retrieve the Franchisee associated with the logged-in user
        franchisee = get_object_or_404(Franchisee, user=user)

        # Retrieve the specific dealer based on the dealer ID and the associated franchisee
        dealer = get_object_or_404(Dealer, id=dealer_id, franchisee=franchisee)

        # Serialize dealer data
        dealer_data = DealerSerializer(dealer)

        return Response(dealer_data.data, status=status.HTTP_200_OK)

class FranchiseeDealerCountView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        franchisee = get_object_or_404(Franchisee, user=user)

        # Count dealers associated with this franchisee
        total_dealers = Dealer.objects.filter(franchisee=franchisee).count()
        active_dealers = Dealer.objects.filter(franchisee=franchisee, status='Active').count()
        inactive_dealers = Dealer.objects.filter(franchisee=franchisee, status='Inactive').count()

        response_data = {
            'total_dealers': total_dealers,
            'active_dealers': active_dealers,
            'inactive_dealers': inactive_dealers,
        }

        return Response(response_data, status=status.HTTP_200_OK)

from .serializers import *
from rest_framework import generics, permissions



class FranchiseeServiceAddView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ServiceRegisterSerializer

    def get_queryset(self):
        # Return all service registers or filter them as needed
        return ServiceRegister.objects.filter(service_provider__user=self.request.user)

    def get(self, request, *args, **kwargs):
        service_providers = ServiceProvider.objects.filter(user=request.user)
        serializer = self.serializer_class(service_providers, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        try:
            service_provider = ServiceProvider.objects.get(user=self.request.user)
            serializer.save(service_provider=service_provider)
        except ServiceProvider.DoesNotExist:
            return Response({'error': 'ServiceProvider does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# from django.shortcuts import get_object_or_404
# from rest_framework import generics
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.filters import SearchFilter  # Add SearchFilter import
# from Accounts.models import ServiceProvider, Franchisee  # Import Franchise model
# from .serializers import ServiceProviderSerializer

# class FranchiseServiceProviderListView(generics.ListAPIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer_class = ServiceProviderSerializer
#     filter_backends = [SearchFilter]  # Enable search functionality
#     search_fields = ['user__full_name', 'user__phone_number', 'user__district__name']  # Define search fields

#     def get_queryset(self):
#         user = self.request.user  # Get the logged-in user
#         franchisee = get_object_or_404(Franchisee, user=user)  # Ensure the user is a franchise
#         return ServiceProvider.objects.filter(franchisee=franchisee)  # Filter by franchise


# from rest_framework import generics
# from .serializers import CreateServiceProviderSerializer
# from .permission import IsFranchiseUser  # Make sure to import your custom permission class


# class ServiceProviderCreateView(generics.CreateAPIView):
#     queryset = ServiceProvider.objects.all()
#     serializer_class = CreateServiceProviderSerializer
#     permission_classes = [IsFranchiseUser]  # Use the custom permission class

#     def perform_create(self, serializer):
#         # Save the ServiceProvider instance with the current user
#         serializer.save(user=self.request.user)


# from rest_framework import generics, permissions
# from .serializers import ServiceProviderAddSerializer
# from rest_framework import generics, permissions, status
# from rest_framework.response import Response
# from rest_framework.authtoken.models import Token

# class AddServiceProviderView(generics.CreateAPIView):
#     serializer_class = ServiceProviderSerializer
#     permission_classes = [permissions.IsAuthenticated]  # Ensure user is authenticated

#     def post(self, request, *args, **kwargs):
#         user = request.user
        
#         # Check if the logged-in user is a franchisee
#         if not user.is_franchisee:
#             return Response({'error': 'Only franchisees can add service providers.'},
#                             status=status.HTTP_403_FORBIDDEN)

#         # Pass validated data to the serializer and save
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response({
#             'message': 'Service provider created successfully.',
#             'service_provider': serializer.data,
#         }, status=status.HTTP_201_CREATED)

from rest_framework import generics, status
from rest_framework.response import Response
from django.db import transaction
from rest_framework.permissions import IsAuthenticated

class DealerCreateView(generics.CreateAPIView):
    serializer_class = AddDealerSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create User first
        user = User.objects.create(
            email=serializer.validated_data.get('email'),
            phone_number=serializer.validated_data['phone_number'],
            full_name=serializer.validated_data['full_name'],
            address=serializer.validated_data['address'],
            pin_code=serializer.validated_data['pin_code'],
            district=serializer.validated_data['district'],
            state=serializer.validated_data['state'],
            is_dealer=True  # Set the role flag
        )
        
        # Create Dealer
        dealer = Dealer.objects.create(
            user=user,
            about=serializer.validated_data['about'],
            profile_image=serializer.validated_data.get('profile_image'),
            service_providers=serializer.validated_data.get('service_providers'),
            franchisee=serializer.validated_data['franchisee'],
            verification_id=serializer.validated_data.get('verification_id'),
            verificationid_number=serializer.validated_data.get('verificationid_number'),
            id_copy=serializer.validated_data.get('id_copy'),
            status='Active'
        )
        
        return Response({
            'message': 'Dealer created successfully',
            'dealer_id': dealer.custom_id,
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
    

class ServiceProviderCreateView(generics.CreateAPIView):
    serializer_class = AddServiceProviderSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create User first
        user = User.objects.create(
            email=serializer.validated_data.get('email'),
            phone_number=serializer.validated_data['phone_number'],
            full_name=serializer.validated_data['full_name'],
            address=serializer.validated_data['address'],
            pin_code=serializer.validated_data['pin_code'],
            district=serializer.validated_data['district'],
            state=serializer.validated_data['state'],
            is_service_provider=True  # Set the role flag
        )
        
        # Create ServiceProvider
        service_provider = ServiceProvider.objects.create(
            user=user,
            about=serializer.validated_data.get('about'),
            profile_image=serializer.validated_data.get('profile_image'),
            date_of_birth=serializer.validated_data['date_of_birth'],
            gender=serializer.validated_data['gender'],
            dealer=serializer.validated_data['dealer'],
            franchisee=serializer.validated_data['franchisee'],
            address_proof_document=serializer.validated_data.get('address_proof_document'),
            id_number=serializer.validated_data.get('id_number'),
            address_proof_file=serializer.validated_data.get('address_proof_file'),
            payout_required=serializer.validated_data['payout_required'],
            status='Active',
            verification_by_dealer='PENDING'
        )
        
        return Response({
            'message': 'Service Provider created successfully',
            'service_provider_id': service_provider.custom_id,
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)