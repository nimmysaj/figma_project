from rest_framework import serializers
from .models import ServiceRequest, Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'invoice_type', 'quantity', 'price', 'total_amount', 'payment_status', 'invoice_date', 'due_date', 'appointment_date']

class ServiceRequestSerializer(serializers.ModelSerializer):
    invoices = InvoiceSerializer(many=True)  # Include related invoices using the related_name

    class Meta:
        model = ServiceRequest
        fields = ['id', 'customer', 'service_provider', 'service', 'work_status', 'acceptance_status', 'request_date', 'availability_from', 'availability_to', 'invoices']