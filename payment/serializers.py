from rest_framework import serializers
from customer.models import Invoice, Payment

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_type', 'service_request', 
            'sender', 'receiver', 'quantity', 'price', 'total_amount', 
            'payment_status', 'invoice_date', 'due_date', 
            'appointment_date', 'additional_requirements', 'accepted_terms'
        ]

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'sender', 'receiver', 'transaction_id', 
            'amount_paid', 'payment_method', 'payment_status', 'payment_date'
        ]
