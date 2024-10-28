from rest_framework import serializers
from Accounts.models import ServiceProviderVerification

from django.contrib.auth import authenticate
from Accounts.models import *
from rest_framework import serializers
from Accounts.models import ServiceProvider
from service_provider.serializers import UserSerializer,ServiceRegisterSerializer
from Accounts.models import User
from rest_framework.exceptions import ValidationError



class DealerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if user is None or not user.is_dealer:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Email and password are required.")

        attrs['user'] = user
        return attrs

class ServiceProviderVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProviderVerification
        fields = '__all__'


class ServiceProviderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    services=ServiceRegisterSerializer(read_only=True,many=True)

    class Meta:
        model = ServiceProvider
        fields = [ "user",
            "profile_image",
            "date_of_birth",
            "gender" ,
            "dealer",
            "franchisee",
            "address_proof_document",
            "id_number", 
            "address_proof_file" ,
            "payout_required", 
            "accepted_terms",
            "services" 
            ]

    def create(self, validated_data):
        # Extract the nested user data from the validated data
        user_data = validated_data.pop('user')

        # Check if accepted_terms is False
        if not validated_data.get('accepted_terms'):
            raise ValidationError({"accepted_terms": "You must accept the terms and conditions to create a profile."})
        
        user = User.objects.create(**user_data)
        service_provider = ServiceProvider.objects.create(user=user, **validated_data)
        return service_provider

    def update(self, instance, validated_data):
        # Extract user data and handle separately
        user_data = validated_data.pop('user', None)

        # Update ServiceProvider fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle User fields separately
        if user_data:
            user = instance.user  # Get the related user instance
            for attr, value in user_data.items():
                if attr == 'email' and user.email:
                    continue  # Skip updating email if it's already set
                if attr == 'phone_number' and user.phone_number:
                    continue  # Skip updating phone number if it's already set
                setattr(user, attr, value)
            user.save()

        # Save the ServiceProvider instance with updated data
        instance.save()
        return instance
    


class DealerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if user is None or not user.is_dealer:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Email and password are required.")

        attrs['user'] = user
        return attrs
    
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
