from rest_framework import serializers
from .models import Invoice, Payment, User

class InvoiceSerializer(serializers.ModelSerializer):
    # Explicitly defining the fields to ensure they are required
    invoice_number = serializers.CharField(required=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    invoice_type = serializers.ChoiceField(choices=Invoice.INVOICE_TYPE_CHOICES, required=True)
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    appointment_date = serializers.DateTimeField(required=True)
    due_date = serializers.DateTimeField(required=True)

    class Meta:
        model = Invoice
        fields = ['invoice_number', 'price', 'invoice_type', 'payment_status', 'sender', 'receiver', 'appointment_date', 'due_date']


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ['invoice', 'payment_id', 'order_id', 'amount']
