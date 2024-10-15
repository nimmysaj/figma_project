from rest_framework import serializers
from .models import Invoice, Payment

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'price', 'invoice_type', 'payment_status', 'sender', 'receiver', 'appointment_date', 'due_date']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['invoice', 'payment_id', 'order_id', 'amount']
