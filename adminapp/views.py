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
from .models import User,Category,Subcategory,Franchisee, Dealer, ServiceProvider, User,Customer,Complaint
from .serializers import UserSerializer,PaginationSerializer,CategorySerializer,CustomerDashboardSerializer
from .serializers import CategoryDashboardSerializer,ComplaintDashboardSerializer,IncompleteBookingsDashboardSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

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

@api_view(['GET'])
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

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer