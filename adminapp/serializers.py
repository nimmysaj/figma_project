from rest_framework import serializers
from .models import ServiceRequest, Invoice,Complaint,CustomerReview

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