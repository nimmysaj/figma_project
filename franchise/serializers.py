from rest_framework import serializers
from django.contrib.auth import authenticate
from Accounts.models import Franchisee, Invoice, PaymentRequest, Payment, Complaint, ServiceRequest



class FranchiseeLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if user is None or not user.is_franchisee:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Email and password are required.")

        attrs['user'] = user
        return attrs
    


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



class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = '__all__'  


class ServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = '__all__' 