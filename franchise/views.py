from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import FranchiseeLoginSerializer
from Accounts.models import Franchisee, PaymentRequest, Complaint, ServiceRequest
from franchise.serializers import FranchiseeSerializer, PaymentRequestSerializer, ServiceRequestSerializer, ComplaintSerializer
from rest_framework import generics, permissions
from django.contrib.auth import authenticate
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404


class FranchiseeLoginView(generics.GenericAPIView):
    serializer_class = FranchiseeLoginSerializer

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
            'is_franchisee': user.is_franchisee,
        }, status=status.HTTP_200_OK)



# To list the  details of the logged-in franchisee

class FranchiseeListView(generics.ListAPIView):
    serializer_class = FranchiseeSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated

    def get_queryset(self):
        # Get the logged-in franchisee
        franchise = Franchisee.objects.get(user=self.request.user)
        # Return the corresponding details of this franchisee
        return Franchisee.objects.filter(id=franchise.id)
    



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Set the default page size
    page_size_query_param = 'page_size'  # Allow clients to set the page size
    max_page_size = 100 



# To list the transaction history of franchisee

class FranchisePaymentHistoryView(generics.ListAPIView):
    serializer_class = PaymentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            # Get the logged-in franchisee
            franchise = Franchisee.objects.get(user=self.request.user)
            # Return payment requests associated with the service providers linked to this franchisee
            return PaymentRequest.objects.filter(service_provider__franchisee=franchise).order_by('-created_at')
        except Franchisee.DoesNotExist:
            raise NotFound("Franchisee not found.")
    



class FranchiseeComplaintsListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        # Get the logged-in franchisee
        franchisee = Franchisee.objects.get(user=self.request.user)
        
        # Filter complaints related to the franchisee
        return Complaint.objects.filter(
            sender=franchisee.user
        ).union(
            Complaint.objects.filter(receiver=franchisee.user)
        ).order_by('-submitted_at')
    


class IncompleteBookingsListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ServiceRequestSerializer

    def get_queryset(self):
        # Get the logged-in franchisee
        franchisee = get_object_or_404(Franchisee, user=self.request.user)
        
        # Get the service providers related to the franchisee
        service_providers = franchisee.serviceprovider_set.all()
        
        # Get the user IDs of the service providers
        service_provider_users = [provider.user.id for provider in service_providers]
        
        # Filter for incomplete bookings based on user IDs
        return ServiceRequest.objects.filter(
            service_provider__id__in=service_provider_users,
            work_status__in=['pending', 'in_progress']
        ).order_by('-request_date')
from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import serializers
from rest_framework import generics
from Accounts.models import User,Dealer,Franchisee
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination

# Create your views here.

# Custom Pagination
class CustomPagination(PageNumberPagination):
    page_size = 6 #Default number of dealers per page
    page_size_query_param = 'page_size' #Allow users to specify page size
    max_page_size = 6

# Combining the two list and return as serializer response
class CombinedDetailsSerializer(serializers.Serializer):
    dealer_details = serializers.ListField(child = serializers.DictField())
    additional_details = serializers.ListField(child = serializers.DictField())

# Percentage Calculation function
class PercentageCalculator:
    @staticmethod
    def calculate_percentage(current_month_count,last_month_count):
        if last_month_count == 0:
            return 100 if current_month_count > 0 else 0
        percentage_change = ((current_month_count - last_month_count)/last_month_count) * 100

        if percentage_change < 0:
            return percentage_change / 100
        else:
            return percentage_change
        
class DealerListView(APIView):
    permission_class =[IsAuthenticated]
   
    def get(self, request,*args, **kwargs):
        try:
            franchisee = Franchisee.objects.get(user_id=request.user.id)
            # Find the Dealers for the authenticated user (franchisee)
            query = Q(franchisee_id = franchisee.id)
            queryset = Dealer.objects.filter(query).order_by('id')
            if not queryset.exists():
                return Response(
                    {"message": "No dealers are added."},
                        status=status.HTTP_404_NOT_FOUND
                )

            # Taken the total dealers,total active dealers,total inactive dealers
            total_dealers = queryset.count()
            total_active_dealers = Dealer.objects.filter(Q(query) & Q(status = 'Active')).count()
            total_inactive_dealers = Dealer.objects.filter(Q(query) & Q(status = 'Inactive')).count()

            # Calculating the Percentage of total dealers
            current_month_dealers = Dealer.objects.filter(Q(query) & Q(created_date__month = timezone.now().month)).count()
            last_month_dealers = Dealer.objects.filter(Q(query) & Q(created_date__month = timezone.now().month -1)).count()
            dealers_percentage=PercentageCalculator.calculate_percentage(current_month_dealers,last_month_dealers)
            
            # Calculating the Percentage of active dealers
            active_query = Q(query) & Q(status = 'Active')
            current_month_active = Dealer.objects.filter(Q(active_query) & Q(created_date__month = timezone.now().month)).count()
            last_month_active = Dealer.objects.filter(Q(active_query) & Q(created_date__month = timezone.now().month-1)).count()
            active_dealers_percentage = PercentageCalculator.calculate_percentage(current_month_active,last_month_active)

            # Calculating the Percentage of Inactive dealers
            inactive_query = Q(query) & Q(status='Inactive')
            current_month_inactive = Dealer.objects.filter(Q(inactive_query) & Q(created_date__month = timezone.now().month)).count()
            last_month_inactive = Dealer.objects.filter(Q(inactive_query) & Q(created_date__month = timezone.now().month-1)).count()
            inactive_dealers_percentage = PercentageCalculator.calculate_percentage(current_month_inactive,last_month_inactive)

            additional_details = []
            additional_details = [
                    {'total_dealers': total_dealers,
                    'total_dealers_perc':dealers_percentage,
                    'total_active': total_active_dealers,
                    'active_dealers_perc':active_dealers_percentage,
                    'total_inactive' : total_inactive_dealers,
                    'inactive_dealers_perc':inactive_dealers_percentage
                    }
            ]
            
            # Taken the details of the Dealers
            # Paginate the dealer_users list
            paginator = CustomPagination()
            paginated_dealers = paginator.paginate_queryset(queryset, request)
            dealer_details = []
            for dealers in paginated_dealers:
                dealer_user = User.objects.get(id=dealers.user_id)
                dealer_profile = Dealer.objects.get(id = dealers.id)
                dealer_details.append({
                        'name':dealer_user.full_name,
                        'custom_id': dealer_profile.custom_id,
                        'service_providers':dealer_profile.service_providers,
                        'location': dealer_user.district.name if dealer_user.district else 'Unknown Location',
                        'contact':dealer_user.phone_number,
                        'email':dealer_user.email,
                        'status':dealer_profile.status,
                })
                serializer = CombinedDetailsSerializer({
                    'additional_details':additional_details,
                    'dealer_details':dealer_details
                })
                
            return Response(serializer.data, status=200)
            
        except Exception as e:
            # Log the error for debugging
            print(f"Error fetching dealers: {e}")
            return Response(
                {"error": "An error occurred while retrieving dealers."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DealerSearchView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access
   
    def get(self,request):
        try:
            franchisee = Franchisee.objects.get(user_id=request.user.id)
            query = request.query_params.get('search',None)
            if not query:
                return Response(
                        {"message": "Please provide dealer name in search bar."},
                        status=status.HTTP_404_NOT_FOUND
                )
            else:
                dealers_list = User.objects.filter(Q(full_name__icontains = query) | Q(district__name__icontains = query)).order_by('id')
                paginator = CustomPagination()
                paginated_dealers = paginator.paginate_queryset(dealers_list, request)   
                dealers_details = []
                for rec in paginated_dealers:
                    try:
                        dealers_profile = Dealer.objects.get(Q(user_id = rec.id) & Q(franchisee_id = franchisee.id))
                        dealer_user = User.objects.get(id = rec.id) 
                        dealers_details.append({
                                'name':dealer_user.full_name,
                                'custom_id': dealers_profile.custom_id,
                                'service_providers':dealers_profile.service_providers,
                                'location': dealer_user.district.name if dealer_user.district else 'Unknown Location',
                                'contact':dealer_user.phone_number,
                                'email':dealer_user.email,
                                'status':dealers_profile.status,
                        }) 
                    except Dealer.DoesNotExist:
                        return Response({"message": "No dealers are added."})
                   
                return Response(dealers_details,status=200)
        except Exception as e:
            # Log the error for debugging
            print(f"Error fetching dealers: {e}")
            return Response(
                {"error": "An error occurred while retrieving dealers."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )            

class DealerSortView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access
    
    def get(self,request):
        try:
            franchisee = Franchisee.objects.get(user_id=request.user.id)
            query = request.query_params.get('search',None)
            sort_by = request.query_params.get('sort_by',None) # sort_by = id(Ascending) ,sort_by = -id(Descending)
            paginator = CustomPagination()
            dealers_details = []
            if query:
                dealers_list = User.objects.filter(Q(full_name__icontains = query) | Q(district__name__icontains = query)).order_by(sort_by) 
                paginated_dealers = paginator.paginate_queryset(dealers_list, request)   
                for rec in paginated_dealers:
                    try:
                        dealers_profile = Dealer.objects.get(Q(user_id = rec.id) & Q(franchisee_id = franchisee.id))
                        dealer_user = User.objects.get(id = rec.id) 
                        dealers_details.append({
                                'name':dealer_user.full_name,
                                'custom_id': dealers_profile.custom_id,
                                'service_providers':dealers_profile.service_providers,
                                'location': dealer_user.district.name if dealer_user.district else 'Unknown Location',
                                'contact':dealer_user.phone_number,
                                'email':dealer_user.email,
                                'status':dealers_profile.status,
                        }) 
                    except Dealer.DoesNotExist:
                        return Response({"message": "No dealers are added."})
            else:
                dealers_list = Dealer.objects.filter(franchisee_id = franchisee.id).order_by(sort_by)
                paginated_dealers = paginator.paginate_queryset(dealers_list, request)
                for dealers in paginated_dealers:
                    try:
                        dealer_user = User.objects.get(id=dealers.user_id)
                        dealer_profile = Dealer.objects.get(id = dealers.id)
                        dealers_details.append({
                                'name':dealer_user.full_name,
                                'custom_id': dealer_profile.custom_id,
                                'service_providers':dealer_profile.service_providers,
                                'location': dealer_user.district.name if dealer_user.district else 'Unknown Location',
                                'contact':dealer_user.phone_number,
                                'email':dealer_user.email,
                                'status':dealer_profile.status,
                        })
                    except Dealer.DoesNotExist:
                        return Response({"message": "No dealers are added."})

            return Response(dealers_details,status=200) 
        except Exception as e:
            # Log the error for debugging
            print(f"Error fetching dealers: {e}")
            return Response(
                {"error": "An error occurred while retrieving dealers."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )            

from django.shortcuts import render

# Create your views here.

from rest_framework import generics,filters,serializers
from Accounts.models import Dealer,ServiceProvider
from franchise.serializers import DealerSerializer,FranchiseeLoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets
from rest_framework.decorators import action
from Dealer.serializers import ServiceProviderSerializer

# get the dealer details, also perform edit function,have search functionality using query params

class DealerdetailView(APIView):
    def get(self,request,*args,**kwargs):
        id=request.data.get("dealer_id")
        dealer=request.query_params.get('dealer')
        if id:
            try:
                qs=Dealer.objects.get(custom_id=id)
                serializer_instance=DealerSerializer(qs)
                return Response(data=serializer_instance.data,status=status.HTTP_200_OK)
            except:
                return Response(data={"message":"Dealer Not found"},status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                qs=Dealer.objects.get(user__full_name=dealer)
                serializer_instance=DealerSerializer(qs)
                return Response(data=serializer_instance.data,status=status.HTTP_200_OK)
            except:
                return Response(data={"message":"Dealer Not found"},status=status.HTTP_400_BAD_REQUEST)
            
    def put(self, request, *args, **kwargs): 
        id = request.data.get("dealer_id") 
        dealer = request.query_params.get('dealer') 
        if id: 
            try: 
                qs = Dealer.objects.get(custom_id=id) 
            except Dealer.DoesNotExist: 
                return Response(data={"message": "Dealer Not found"}, status=status.HTTP_404_NOT_FOUND) 
        elif dealer: 
            try:
                qs = Dealer.objects.get(user__full_name=dealer) 
            except Dealer.DoesNotExist: 
                return Response(data={"message": "Dealer Not found"}, status=status.HTTP_404_NOT_FOUND) 
            else: return Response(data={"message": "Dealer ID or dealer query parameter is required."}, status=status.HTTP_400_BAD_REQUEST) 
        serializer_instance = DealerSerializer(qs, data=request.data, partial=True)
        if serializer_instance.is_valid(): 
            serializer_instance.save() 
            return Response(data=serializer_instance.data, status=status.HTTP_200_OK) 
        else: return Response(data=serializer_instance.errors, status=status.HTTP_400_BAD_REQUEST)


class FranchiseServiceProviderViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__full_name', 'user__district__name']

    @action(detail=False, methods=['post'])
    def services(self, request):
        service_provider_id = request.data.get('service_provider_id')
        
        if not service_provider_id:
            return Response({'error': 'Service Provider ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service_provider = ServiceProvider.objects.get(custom_id=service_provider_id)
        except ServiceProvider.DoesNotExist:
            return Response({'error': 'Service Provider not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(service_provider)
        return Response(serializer.data)