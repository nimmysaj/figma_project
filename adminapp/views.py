from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from .models import ServiceRequest,Customer
from .serializers import ServiceRequestSerializer
from django.core.paginator import Paginator
from .pagination import CustomPagination
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import User,Category,Subcategory,Franchisee, Dealer, ServiceProvider, User,Customer,Complaint,Payment,Invoice
from .serializers import UserSerializer,PaginationSerializer,CategorySerializer,CustomerDashboardSerializer
from .serializers import CategoryDashboardSerializer,ComplaintDashboardSerializer,IncompleteBookingsDashboardSerializer
from .serializers import CustomerStatusTotalsSerializer, PaymentTotalsSerializer, MonthlyComparisonSerializer, YearlyIncomeExpenseSerializer
from .serializers import LoginSerializer

from django.db.models import Sum
from django.utils import timezone
from django.db.models import Count
import calendar
from django.db.models.functions import TruncDate
from django.utils.timezone import now


class ServiceRequestDetailView(APIView):
    def post(self, request, *args, **kwargs):
        
        service_request_id = request.data.get('service_request_id')

        
        if not service_request_id:
            return Response({"error": "Service request ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        
        service_request = get_object_or_404(ServiceRequest, id=service_request_id)

        # Serialize the service request, including the related invoices, reviews, and complaints
        serializer = ServiceRequestSerializer(service_request)

        # Return the serialized data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailsView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        

class UserPaymentHistoryView(APIView):
        
    def post(self, request, *args, **kwargs):
        users_id = request.data.get('users_id')  # Get user ID from request data

        if not users_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Filter service requests for the specified user
        queryset =  User.objects.filter(id=users_id)

        # Apply pagination
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Serialize the paginated data
        serializer =UserSerializer(paginated_queryset, many=True)

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)
        

@api_view(['GET', 'POST'])
def category_list(request):
    # Handle GET request
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)

        # Prepare custom response with counts
        response_data = {
            'total_categories': Category.objects.count(),
            'total_subcategories': Subcategory.objects.count(),  # Assuming Subcategory model exists
            'categories': serializer.data  # Include the actual list of categories
        }

        return Response(response_data)  # This is reachable now

    # Handle POST request
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT', 'PATCH', 'DELETE'])
def category_detail(request):
    # Get the 'id' from the request body.
    category_id = request.data.get('id')

    if not category_id:
        return Response({"error": "ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
       
    
class CustomPagination(PageNumberPagination):
    page_size = 3  # Number of items per page
    page_size_query_param = 'page_size'  # Allow client to specify page size
    max_page_size = 100  # Limit max page size


def dashboard_view(request):
    # Determine the type of data requested
    data_type = request.query_params.get('type', '').strip().lower()

    # Define the range for recent customers
    recent_days = 7
    recent_date = datetime.now() - timedelta(days=recent_days)

    # Fetch totals
    total_franchisees = Franchisee.objects.count()
    total_dealers = Dealer.objects.count()
    total_service_providers = ServiceProvider.objects.count()
    total_customers = Customer.objects.count()

    if data_type == 'recent_customers':
        # Fetch recent customers and return their data
        recent_customers = Customer.objects.filter(
            user_created_at_gte=recent_date,
            status='Active'
        ).order_by('-user__created_at')

        paginator = CustomPagination()
        paginated_customers = paginator.paginate_queryset(recent_customers, request)

        customer_serializer = CustomerDashboardSerializer(paginated_customers, many=True)
        return paginator.get_paginated_response(customer_serializer.data)

    elif data_type == 'categories':
        # Fetch categories and return their data
        categories = Category.objects.all()
        paginator = CustomPagination()
        paginated_categories = paginator.paginate_queryset(categories, request)

        category_serializer = CategoryDashboardSerializer(paginated_categories, many=True)
        return paginator.get_paginated_response(category_serializer.data)

    elif data_type == 'complaints':
        # Fetch complaints and return their data
        complaints = Complaint.objects.all().order_by('-submitted_at')
        paginator = CustomPagination()
        paginated_complaints = paginator.paginate_queryset(complaints, request)

        complaints_serializer = ComplaintDashboardSerializer(paginated_complaints, many=True)
        return paginator.get_paginated_response(complaints_serializer.data)

    elif data_type == 'incomplete_bookings':
        # Fetch incomplete bookings and return their data
        service_request = ServiceRequest.objects.filter(
            acceptance_status='pending'
        ).order_by('-request_date')
        paginator = CustomPagination()
        paginated_service_requests = paginator.paginate_queryset(service_request, request)

        service_request_serializer = IncompleteBookingsDashboardSerializer(paginated_service_requests, many=True)
        return paginator.get_paginated_response(service_request_serializer.data)

    # Default response with combined data if no specific type is provided
    recent_customers = Customer.objects.filter(
        user__created_at__gte=recent_date,
        status='Active'
    ).order_by('-user__created_at')

    paginator = CustomPagination()
    paginated_customers = paginator.paginate_queryset(recent_customers, request)
    customer_serializer = CustomerDashboardSerializer(paginated_customers, many=True)

    categories = Category.objects.all()
    paginated_categories = paginator.paginate_queryset(categories, request)
    category_serializer = CategoryDashboardSerializer(paginated_categories, many=True)

    complaints = Complaint.objects.all().order_by('-submitted_at')
    paginated_complaints = paginator.paginate_queryset(complaints, request)
    complaints_serializer = ComplaintDashboardSerializer(paginated_complaints, many=True)

    service_request = ServiceRequest.objects.filter(
        acceptance_status='pending'
    ).order_by('-request_date')
    paginated_service_requests = paginator.paginate_queryset(service_request, request)
    service_request_serializer = IncompleteBookingsDashboardSerializer(paginated_service_requests, many=True)

    response_data = {
        'Total_Franchisees': total_franchisees,
        'Total_Dealers': total_dealers,
        'Total_Service_Providers': total_service_providers,
        'Total_Customers': total_customers,
        'Recent_Activities': customer_serializer.data,
        'Categories': category_serializer.data,
        'Complaints': complaints_serializer.data,
        'Incomplete_Bookings': service_request_serializer.data
    }

    return Response(response_data)

class TotalCountsView(APIView):
    """Fetch total counts for dashboard overview."""
    def get(self, request, *args, **kwargs):
        data = {
            "total_franchisees": Franchisee.objects.count(),
            "total_dealers": Dealer.objects.count(),
            "total_service_providers": ServiceProvider.objects.count(),
            "total_customers": Customer.objects.count(),
        }
        return Response(data)
    
class RecentCustomersView(APIView):
    """Fetch recent customers created in the last 7 days."""
    def get(self, request, *args, **kwargs):
        recent_days = 7
        recent_date = now() - timedelta(days=recent_days)
        recent_customers = Customer.objects.filter(
            user__created_at__gte=recent_date,
            status='Active'
        ).order_by('-user__created_at')
        
        paginator = CustomPagination()
        paginated_customers = paginator.paginate_queryset(recent_customers, request)
        customer_serializer = CustomerDashboardSerializer(paginated_customers, many=True)
        return paginator.get_paginated_response(customer_serializer.data)

class CategoriesView(APIView):
    """Fetch all categories."""
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        paginator = CustomPagination()
        paginated_categories = paginator.paginate_queryset(categories, request)
        category_serializer = CategoryDashboardSerializer(paginated_categories, many=True)
        return paginator.get_paginated_response(category_serializer.data)

class ComplaintsView(APIView):
    """Fetch all complaints."""
    def get(self, request, *args, **kwargs):
        complaints = Complaint.objects.all().order_by('-submitted_at')
        paginator = CustomPagination()
        paginated_complaints = paginator.paginate_queryset(complaints, request)
        complaints_serializer = ComplaintDashboardSerializer(paginated_complaints, many=True)
        return paginator.get_paginated_response(complaints_serializer.data)

class IncompleteBookingsView(APIView):
    """Fetch incomplete bookings with pending acceptance status."""
    def get(self, request, *args, **kwargs):
        service_requests = ServiceRequest.objects.filter(
            acceptance_status='pending'
        ).order_by('-request_date')
        
        paginator = CustomPagination()
        paginated_service_requests = paginator.paginate_queryset(service_requests, request)
        service_request_serializer = IncompleteBookingsDashboardSerializer(paginated_service_requests, many=True)
        return paginator.get_paginated_response(service_request_serializer.data)

#login
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PerformanceGraphView(APIView):
     def post(self, request):
        admin_user_id = request.data.get('admin_user_id')
        year = request.data.get('year')

        if not admin_user_id:
            return Response({"detail": "Admin user ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not year:
            return Response({"detail": "Year is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except ValueError:
            return Response({"detail": "Year must be a valid integer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin_user = User.objects.get(id=admin_user_id)
        except User.DoesNotExist:
            return Response({"detail": "Admin user not found."}, status=status.HTTP_404_NOT_FOUND)

        yearly_comparison = []

        # Loop through each month of the specified year
        for month in range(1, 13):
            start_date = now().replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = (start_date + timedelta(days=31)).replace(day=1)

            payments = Payment.objects.filter(payment_date__gte=start_date, payment_date__lt=end_date)

            # Calculate income and expenses for the month
            monthly_income = payments.filter(receiver=admin_user).aggregate(
                total_income=Sum('amount_paid'))['total_income'] or 0

            monthly_expense = payments.filter(sender=admin_user).aggregate(
                total_expense=Sum('amount_paid'))['total_expense'] or 0

            yearly_comparison.append({
                "month": start_date.strftime("%B"),  
                "income": monthly_income,
                "expense": monthly_expense
            })

        data = {"yearly_comparison": yearly_comparison}

        return Response(data, status=status.HTTP_200_OK)
 
class FinancesGraphView(APIView):
    def get(self, request, *args, **kwargs):
        today = now().date()

        # Determine the start of the current week (Monday)
        start_of_week = today - timedelta(days=today.weekday())

        # Determine the start of the previous week (Monday)
        start_of_last_week = start_of_week - timedelta(days=7)

        # Prepare lists to hold the financial totals and days
        current_week_data = []
        last_week_data = []

        # Calculate totals for the current week
        for i in range(7):  # Loop through each day of the current week
            date = start_of_week + timedelta(days=i)
            total_for_day = Invoice.objects.filter(
                invoice_date__date=date  # Use the correct date field
            ).aggregate(total_amount=Sum('total_amount'))['total_amount'] or 0

            # Append the day and total to the current week data
            current_week_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'day': date.strftime('%A'),  # Get the name of the day
                'total_amount': total_for_day
            })

        # Calculate totals for the last week
        for i in range(7):
            date = start_of_last_week + timedelta(days=i)
            total_for_day = Invoice.objects.filter(
                invoice_date__date=date  # Use the correct date field
            ).aggregate(total_amount=Sum('total_amount'))['total_amount'] or 0

            # Append the day and total to the last week data
            last_week_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'day': date.strftime('%A'),  # Get the name of the day
                'total_amount': total_for_day
            })

        # Prepare the response data
        response_data = {
            'current_week_totals': current_week_data,
            'last_week_totals': last_week_data
        }

        return Response(response_data)
    
class CustomerArrivalGraphView(APIView):
    # Add appropriate permissions

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()

        # Calculate the first and last day of the previous two months
        first_day_last_month = (today.replace(day=1) - timezone.timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timezone.timedelta(days=1)

        first_day_two_months_ago = (first_day_last_month - timezone.timedelta(days=1)).replace(day=1)
        last_day_two_months_ago = first_day_last_month - timezone.timedelta(days=1)

        # Format month names
        last_month_name = calendar.month_name[first_day_last_month.month]
        two_months_ago_name = calendar.month_name[first_day_two_months_ago.month]

        # Query for the second-last month
        registrations_two_months_ago = (
            User.objects.filter(
                created_at__date__gte=first_day_two_months_ago,
                created_at__date__lte=last_day_two_months_ago,
                is_customer=True
            )
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(registration_count=Count('id'))
            .order_by('date')
        )

        # Query for the last month
        registrations_last_month = (
            User.objects.filter(
                created_at__date__gte=first_day_last_month,
                created_at__date__lte=last_day_last_month,
                is_customer=True
            )
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(registration_count=Count('id'))
            .order_by('date')
        )

        # Create a function to ensure all dates in a range are represented
        def fill_missing_dates(start_date, end_date, registrations):
            all_dates = {}
            # Initialize all dates in the range with a count of 0
            current_date = start_date
            while current_date <= end_date:
                all_dates[current_date] = 0
                current_date += timezone.timedelta(days=1)

            # Update with actual registration counts
            for registration in registrations:
                all_dates[registration['date']] = registration['registration_count']
            
            # Convert to list of dictionaries for response format
            return [{'date': date, 'registration_count': count} for date, count in all_dates.items()]

        # Fill in missing dates for each month
        data = {
            last_month_name: fill_missing_dates(first_day_last_month, last_day_last_month, registrations_last_month),
            two_months_ago_name: fill_missing_dates(first_day_two_months_ago, last_day_two_months_ago, registrations_two_months_ago),
        }

        return Response(data)
   
class StatisticsGraphView(APIView):
    def get(self, request, *args, **kwargs):
        # Calculate the counts for active and inactive customers
        active_customers = Customer.objects.filter(status='Active').count()
        inactive_customers = Customer.objects.filter(status='Inactive').count()

        # Prepare data for the response
        data = {
            'active_customers': active_customers,
            'inactive_customers': inactive_customers,
        }

        return Response(data)

class RevenueGraphView(APIView):
    def get(self, request):
        # Filter and calculate the sum for the specified invoice types
        total_ads = Invoice.objects.filter(invoice_type="Ads").aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_service_request = Invoice.objects.filter(invoice_type="service_request").aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_service_registration = Invoice.objects.filter(invoice_type="service_registration").aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # Total of all specified types
        total_all = total_ads + total_service_request + total_service_registration

        # Calculate percentages
        def calculate_percentage(value, total):
            return round((value / total * 100), 2) if total > 0 else 0

        data = {
            'total_ads': total_ads,
            'total_ads_percentage': calculate_percentage(total_ads, total_all),
            'total_service_request': total_service_request,
            'total_service_request_percentage': calculate_percentage(total_service_request, total_all),
            'total_service_registration': total_service_registration,
            'total_service_registration_percentage': calculate_percentage(total_service_registration, total_all),
            'total_all': total_all
        }
        
        return Response(data)