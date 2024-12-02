from rest_framework.response import Response
from rest_framework import generics
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from Accounts.models import Franchisee, Franchise_Type, Category, Subcategory
from .serializers import FranchiseeSerializer, CategorySerializer
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from django.db.models import Q
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from Accounts.models import ServiceRequest
from .serializers import ServiceRequestDetailSerializer
from rest_framework.exceptions import NotFound
from customer.permissions import IsOwnerOrAdmin
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from rest_framework import generics,status,permissions,authentication,views
from Accounts.models import Customer,Country_Codes,State,District,GENDER_CHOICES,Franchisee,ServiceProvider,Dealer,ServiceRequest,Complaint,Invoice,Payment,Ad_category,Ad_Management
from rest_framework.response import Response
from Admin.serializers import CustomerSerializer,BookingSerializer,ComplaintSerializer,AdsManagementSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum
from datetime import datetime, timedelta 
import calendar
from rest_framework import filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,BasePermission


class FranchiseeFilter(filters.FilterSet):
    # Search by franchisee name (username) and community name
    name = filters.CharFilter(field_name="user__full_name", lookup_expr="icontains", label="Franchisee Name")
    community_name = filters.CharFilter(field_name="community_name", lookup_expr="icontains", label="Community Name")
    
    # Filter by Franchise Type
    franchisee_type = filters.ModelChoiceFilter(queryset=Franchise_Type.objects.all(), field_name="type", label="Franchisee Type")

    # Sorting based on creation date
    sort_by_date = filters.OrderingFilter(
        fields=(('valid_from', 'Date Added'),),  # Sort by the 'valid_from' field (ascending by default)
        field_labels={'valid_from': 'Date Added'}
    )

    class Meta:
        model = Franchisee
        fields = ['name', 'community_name', 'franchisee_type']


class FranchiseePagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


class FranchiseeListView(generics.ListAPIView):
    queryset = Franchisee.objects.all()
    serializer_class = FranchiseeSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = FranchiseeFilter
    search_fields = ['user__full_name', 'community_name']  # Add search fields for community name and franchisee name

    # Use the local pagination class here
    pagination_class = FranchiseePagination

    def get_queryset(self):
        """
        Apply filters and search to the queryset.
        """
        queryset = super().get_queryset()

        # Apply search filters based on the query parameters
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(user__full_name__icontains=search_query) | Q(community_name__icontains=search_query)
            )

        # Apply other filters if any
        queryset = self.filter_queryset(queryset)

        # Handle ordering by date (newest first)
        order_by = self.request.query_params.get('ordering', '-valid_from')  # Default to '-valid_from' for descending
        queryset = queryset.order_by(order_by)

        return queryset

    def get_previous_month_counts(self, queryset):
        """
        Get the counts from the previous month for comparison.
        """
        today = datetime.today()
        # Get the first day of the current month
        first_day_of_current_month = today.replace(day=1)
        # Get the last day of the previous month
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

        # Get counts for the previous month
        previous_month_queryset = queryset.filter(
            valid_from__gte=first_day_of_previous_month,
            valid_from__lt=first_day_of_current_month
        )
        
        previous_month_total = previous_month_queryset.count()
        previous_month_active = previous_month_queryset.filter(status='Active').count()
        previous_month_inactive = previous_month_queryset.filter(status='Inactive').count()

        return previous_month_total, previous_month_active, previous_month_inactive

    def calculate_percentage_difference(self, current, previous):
        """
        Calculate percentage difference between current and previous counts.
        Returns 0 if the previous count is 0 to avoid division by zero.
        """
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100

    def list(self, request, *args, **kwargs):
        """
        Override the list method to add the total number of franchisees, 
        active franchisees, inactive franchisees, and their percentage 
        differences from the past month. 
        This will always be based on the full (unfiltered) dataset.
        """
        # Get the unfiltered queryset (all franchisees)
        unfiltered_queryset = Franchisee.objects.all()

        # Get the total counts for the unfiltered queryset
        total_count = unfiltered_queryset.count()
        active_count = unfiltered_queryset.filter(status='Active').count()
        inactive_count = unfiltered_queryset.filter(status='Inactive').count()

        # Get the previous month's counts for comparison
        previous_month_total, previous_month_active, previous_month_inactive = self.get_previous_month_counts(unfiltered_queryset)

        # Calculate the percentage differences based on the unfiltered dataset
        total_percentage_change = self.calculate_percentage_difference(total_count, previous_month_total)
        active_percentage_change = self.calculate_percentage_difference(active_count, previous_month_active)
        inactive_percentage_change = self.calculate_percentage_difference(inactive_count, previous_month_inactive)

        # Get the filtered queryset (for pagination)
        queryset = self.get_queryset()

        # Paginate the current queryset (filtered)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # Returning the paginated response with the counts and percentage differences based on unfiltered data
            return self.get_paginated_response({
                'total_franchisees': total_count,
                'total_franchisees_percentage_change': total_percentage_change,

                'active_franchisees': active_count,
                'active_franchisees_percentage_change': active_percentage_change,

                'inactive_franchisees': inactive_count,
                'inactive_franchisees_percentage_change': inactive_percentage_change,
                
                'results': serializer.data
            })

        # If not paginating, return all data with counts and percentage differences
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'total_franchisees': total_count,
            'total_franchisees_percentage_change': total_percentage_change,

            'active_franchisees': active_count,
            'active_franchisees_percentage_change': active_percentage_change,

            'inactive_franchisees': inactive_count,
            'inactive_franchisees_percentage_change': inactive_percentage_change,

            'results': serializer.data
        })



class CategoryFilter(filters.FilterSet):
    category = filters.CharFilter(field_name= 'title', lookup_expr="icontains", label="categoryName")

    # Filter by category title
    category_type = filters.ModelChoiceFilter(queryset=Category.objects.all(), field_name="type", label="category type")
   
    # sorting based on cretion date
    sort_by_date = filters.OrderingFilter(
        fields = (('created_at', 'Date added'),),
        field_labels = {'created_at':'Date Added' }
    )
    class Meta:
        model = Category
        fields = ['title', 'category_type']

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    search_fields = ['title']
    filterset_class = CategoryFilter

    def get_queryset(self):
        queryset = super().get_queryset()

        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
            )

        queryset = self.filter_queryset(queryset)

        # Handle ordering by date (newest first)
        order_by = self.request.query_params.get('ordering', '-created_at')  # Default to '-created_at' for descending
        queryset = queryset.order_by(order_by)
        return queryset
    
    def list(self, request, *args, **kwargs):
        category_queryset = Category.objects.all()
        subcategory_queryset = Subcategory.objects.all()

        # get the counts of category and subcategory

        category_count = category_queryset.count()
        subcategory_count = subcategory_queryset.count()
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True )
        return Response({
            'total category': category_count,
            'total subcategory': subcategory_count,

            'results': serializer.data

        })

# Create your views here.

class CustomerServiceRequestsView(APIView):
    
    permission_classes = [] 

    """
    API View to get all service requests for a particular customer.
    """

    def get(self, request, servicerequest_id, *args, **kwargs):
        """
        Get all service requests for the given customer ID, along with associated complaints, invoices, and reviews.
        """
        # Filter ServiceRequests by servicerequest_id
        try:
           
            service_requests = ServiceRequest.objects.filter(id=servicerequest_id)  
            
        except ServiceRequest.DoesNotExist:
            raise NotFound("Service requests not found for the given servicerequest ID.")
        
        # Serialize the service requests along with their nested data
        serializer = ServiceRequestDetailSerializer(service_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class IsAdminUser(BasePermission):
    def has_permission(self, request, view): # Check if the user is authenticated and is a superuser 
        return request.user and (request.user.is_superuser)

#pagination classes
class IncompleteBookingPaginator(PageNumberPagination):
    page_size=5
    page_query_param='page'
    max_page_size=5

class ComplaintPaginator(PageNumberPagination):
    page_size=6
    page_query_param='page'
    max_page_size=6

# Create your views here.

class AddNewUserView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get(self, request, *args, **kwargs):
        country_codes=Country_Codes.objects.all().values('country_name', 'calling_code','id')
        state=State.objects.all().values('name','id')
        district=District.objects.all().values('name','state','id')
        
        return Response({
            'gender_choices':GENDER_CHOICES,
            'country_codes':list(country_codes),
            'states':list(state),
            'districts':list(district)
        })

    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class AdminDashBoardView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request,*args,**kwargs):
        total_franchise=Franchisee.objects.all().count()
        total_service_providers=ServiceProvider.objects.filter(status="Active",verification_by_dealer="APPROVED").count()
        total_dealers=Dealer.objects.all().count()
        total_users=Customer.objects.all().count()
        
        data={
            'total_franchise':total_franchise,
            'total_service_providers':total_service_providers,
            'total_dealers':total_dealers,
            'total_users':total_users
            }

        return Response(data=data)


class IncompleteBookingView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=BookingSerializer
    queryset=ServiceRequest.objects.filter(work_status='pending').order_by('id')
    pagination_class=IncompleteBookingPaginator

class ComplaintsView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    queryset=Complaint.objects.all().order_by('id')
    serializer_class=ComplaintSerializer
    pagination_class=ComplaintPaginator

class AdsManagementDashBoardView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    def get(self,request,*args,**kwargs):
        today = datetime.today() 
        current_month_start = today.replace(day=1) 
        current_month_end = today  
        first_day_of_current_month = today.replace(day=1) 
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1) 
        previous_month_start = last_day_of_previous_month.replace(day=1) 
        previous_month_end = last_day_of_previous_month
        current_month_revenue = Payment.objects.filter( invoice__invoice_type='Ads', payment_date__range=[current_month_start, current_month_end] ).aggregate(total_revenue=Sum('amount_paid'))['total_revenue'] or 0.0
        previous_month_revenue = Payment.objects.filter( invoice__invoice_type='Ads', payment_date__range=[previous_month_start, previous_month_end] ).aggregate(total_revenue=Sum('amount_paid'))['total_revenue'] or 0.0
        #total_ads_revenue = Payment.objects.filter( invoice__invoice_type='Ads' ).aggregate(total_revenue=Sum('amount_paid'))['total_revenue'] or 0.0
        total_ads=Ad_Management.objects.filter(created_date__range=[current_month_start, current_month_end]).count()
        other_ad=['banner','pop_up','card']
        other_ads=Ad_Management.objects.filter(created_date__range=[current_month_start, current_month_end],ad_category__ad_type__in=other_ad).count()
        current_month_ads = Ad_Management.objects.filter( created_date__range=[current_month_start, current_month_end],ad_category__ad_type__in=other_ad ).count() 
        previous_month_ads = Ad_Management.objects.filter( created_date__range=[previous_month_start, previous_month_end],ad_category__ad_type__in=other_ad ).count()
        if previous_month_ads > 0: 
            ads_percentage_difference = ((current_month_ads - previous_month_ads) / previous_month_ads) * 100 
            ads_change_type = "increase" if ads_percentage_difference > 0 else "decrease" 
        else: 
            ads_percentage_difference = 100.0 if current_month_ads > 0 else 0.0 
            ads_change_type = "increase" if current_month_ads > 0 else "no change"
        if previous_month_revenue > 0: 
            percentage_difference = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100 
            change_type = "increase" if percentage_difference > 0 else "decrease"
        else: 
            percentage_difference = 100.0 if current_month_revenue > 0 else 0.0
            change_type = "increase" if current_month_revenue > 0 else "no change"

        profile_boost=Ad_Management.objects.filter(created_date__range=[current_month_start, current_month_end],ad_category__ad_type='profile_boost').count()
        current_month_boost_ads = Ad_Management.objects.filter( created_date__range=[current_month_start, current_month_end],ad_category__ad_type='profile_boost').count() 
        previous_month_boost_ads = Ad_Management.objects.filter( created_date__range=[previous_month_start, previous_month_end],ad_category__ad_type='profile_boost').count()
        if previous_month_boost_ads > 0: 
            boost_ads_percentage_difference = ((current_month_boost_ads - previous_month_boost_ads) / previous_month_boost_ads) * 100 
            boost_ads_change_type = "increase" if boost_ads_percentage_difference > 0 else "decrease" 
        else: 
            boost_ads_percentage_difference = 100.0 if current_month_boost_ads > 0 else 0.0 
            boost_ads_change_type = "increase" if current_month_boost_ads > 0 else "no change"

            data={
                'total_ads':{
                    'ads':total_ads,
                    'difference':ads_percentage_difference,
                    'chage_type':ads_change_type
                },
                'ads_revenue':{
                'total_ads_revenue':current_month_revenue,
                'percentage_diff':percentage_difference,
                'change_type':change_type},
                'other_ads':{
                    'other_ad_count':other_ads,
                    'difference':ads_percentage_difference,
                    'diff_type':ads_change_type
                },
                'profile_boost':{
                    'profile_boost_count':profile_boost,
                    'difference':boost_ads_percentage_difference,
                    'diff_type':boost_ads_change_type
                }
                }

        return Response(data=data)
    

class AdsCategoryView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    def get(self,request,*args,**kwargs):
        qs=Ad_category.objects.all().values_list('ad_type')

        return Response(data={'ads_category':qs})


class AdsManagementView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class=AdsManagementSerializer
    queryset=Ad_Management.objects.all()
    filter_backends=[filters.SearchFilter]
    search_fields=['ad_category__ad_type']