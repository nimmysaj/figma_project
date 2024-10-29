from rest_framework import serializers
from .models import ServiceRequest, Invoice,Complaint,CustomerReview,Payment,Category,Customer
from .models import User, District, State, Country_Codes


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'invoice_type', 'quantity', 'price', 'total_amount', 'payment_status', 'invoice_date', 'due_date', 'appointment_date']

class CustomerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerReview
        fields = ['id', 'customer', 'service_provider', 'rating', 'image', 'comment', 'created_at']
        

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            'id', 'customer', 'service_provider', 'service_request', 'subject', 
            'description', 'images', 'submitted_at', 'status', 'resolved_at', 'resolution_notes'
        ]


class ServiceRequestSerializer(serializers.ModelSerializer):
    invoices = InvoiceSerializer(many=True)  # Related invoices
    reviews = CustomerReviewSerializer(many=True)  # Related reviews
    complaints = ComplaintSerializer(many=True)  # Related complaints

    class Meta:
        model = ServiceRequest
        fields = ['id', 'customer', 'service_provider', 'service', 'work_status', 'acceptance_status', 'request_date', 'availability_from', 'availability_to','invoices','reviews', 'complaints']


class ServiceRequestOnlySerializer(serializers.ModelSerializer):
    
    service_provider_name=serializers.CharField(source='user.full_name')
    service_details=serializers.CharField(source='service.description')
    
    class Meta:
        model = ServiceRequest
        fields = ['id',  'service_provider','service_provider_name', 'service','service_details', 'acceptance_status', 'request_date']


class PaymentSerializer(serializers.ModelSerializer):
    # Displaying sender and receiver details
    
    class Meta:
        model = Payment
        fields = ['transaction_id', 'amount_paid',  'payment_date', 'payment_status']

        
class UserSerializer(serializers.ModelSerializer):
    
    service_requests = ServiceRequestOnlySerializer(many=True, read_only=True, source='servicerequest_set')
    payment_history = serializers.SerializerMethodField()

    
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'email', 'phone_number', 'address', 'landmark', 'pin_code',
            'district', 'state', 'watsapp', 'country_code','payment_history','service_requests',
        ]
    
    # To represent foreign key fields with their string representation:
    district = serializers.StringRelatedField()
    state = serializers.StringRelatedField()
    country_code = serializers.StringRelatedField()
  
    def get_payment_history(self, obj):
        payments = Payment.objects.filter(user=obj)
        return PaymentSerializer(payments, many=True).data
    
    def get_service_requests(self, obj):
        service_request = ServiceRequest.objects.filter(user=obj)
        return ServiceRequestOnlySerializer(service_request, many=True).data
    
    
class PaginationSerializer(serializers.Serializer):
    
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=10)

    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title','image','description', 'status']

        
class CustomerDashboardSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.full_name')  # Fetch full_name from User model
    
    profile_image = serializers.SerializerMethodField()
    date = serializers.DateTimeField(source='user.created_at') 
    location=serializers.CharField(source='user.district')
    
    class Meta:
        model = Customer
        fields = ['name', 'profile_image', 'location', 'date']

    def get_profile_image(self, obj):
        # Safely get the request object from the context
        request = self.context.get('request', None)
        if obj.profile_image:
            # Check if request exists, then build the absolute URI
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url  # Return relative URL if request is None
        return None
    
    
class IncompleteBookingsDashboardSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='user.full_name', read_only=True)
    service_provider_name = serializers.CharField(source='service_provider.full_name', read_only=True)
    profile_image = serializers.SerializerMethodField()
    

    class Meta: 
        model = ServiceRequest
        fields = ['id','profile_image','customer_name','service_provider_name', 'request_date','acceptance_status']

    def get_profile_image(self, obj):
        # Ensure that request is available in the context
        request = self.context.get('request', None)
        
        try:
            # Attempt to retrieve the related Customer profile image
            customer = Customer.objects.get(user=obj.customer)
            if customer.profile_image:
                # Return an absolute URI if request exists; otherwise, return the relative URL
                if request:
                    return request.build_absolute_uri(customer.profile_image.url)
                return customer.profile_image.url  # Return relative URL
        except Customer.DoesNotExist:
            pass  # If Customer does not exist, default to None
        
        return None
    
        
class ComplaintDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['id', 'customer' ,'submitted_at', 'status' ]


class CategoryDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title','image']