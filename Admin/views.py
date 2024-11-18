from rest_framework.response import Response
from rest_framework import generics
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from Accounts.models import Franchisee, Franchise_Type, Category, Subcategory
from .serializers import FranchiseeSerializer, CategorySerializer
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from django.db.models import Q


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