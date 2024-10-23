from rest_framework import serializers
from Accounts.models import Dealer, Franchisee, Franchise_Type, PaymentRequest, Invoice, Payment

class FranchiseeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Franchisee
        fields = '__all__'



class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'total_amount', 'payment_status', 'invoice_date']  

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'payment_date', 'payment_status', 'transaction_id']  

class PaymentRequestSerializer(serializers.ModelSerializer):
    invoices = InvoiceSerializer(many=True, read_only=True)  
    payments = PaymentSerializer(many=True, read_only=True)  

    class Meta:
        model = PaymentRequest
        fields = '__all__' 