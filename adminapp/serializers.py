from rest_framework import serializers
from .models import ServiceRequest, Invoice,Complaint,CustomerReview,Payment
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

class PaymentSerializer(serializers.ModelSerializer):
    # Displaying sender and receiver details
    
    class Meta:
        model = Payment
        fields = ['transaction_id', 'sender', 'receiver', 'amount_paid', 'payment_method', 'payment_date', 'payment_status']
        
class ServiceRequestOnlySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ServiceRequest
        fields = ['id', 'customer', 'service_provider', 'service', 'work_status', 'acceptance_status', 'request_date', 'availability_from', 'availability_to']
        
        
class UserSerializer(serializers.ModelSerializer):
    
    service_requests = ServiceRequestOnlySerializer(many=True, read_only=True, source='servicerequest_set')
    payment_history = serializers.SerializerMethodField()
    
    
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'email', 'phone_number', 'address', 'landmark', 'pin_code',
            'district', 'state', 'watsapp', 'country_code', 'is_customer', 
            'is_service_provider', 'is_franchisee', 'is_dealer', 'is_active', 
            'is_superuser', 'is_staff','payment_history','service_requests',
        ]
    
    # To represent foreign key fields with their string representation:
    district = serializers.StringRelatedField()
    state = serializers.StringRelatedField()
    country_code = serializers.StringRelatedField()

    # Customizing the representation if needed:
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['display_name'] = instance.full_name or instance.email
        return representation
    
    def get_payment_history(self, obj):
        payments = Payment.objects.filter(user=obj)
        return PaymentSerializer(payments, many=True).data
    
    
    def get_service_requests(self, obj):
        servicerequest = ServiceRequest.objects.filter(user=obj)
        return ServiceRequestOnlySerializer(servicerequest, many=True).data