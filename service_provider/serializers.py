from rest_framework import serializers
from Accounts.models import (
    ServiceRequest, 
    User, 
    Invoice
    )
from django.contrib.auth import authenticate


class ServiceRequestSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    subcategory = serializers.CharField(source='service.subcategory', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'customer_name', 'subcategory', 'acceptance_status', 'request_date', 
            'availability_from', 'availability_to','image'
        ]


class CustomerServiceRequestSerializer(serializers.ModelSerializer):
    serviceprovider = serializers.CharField(source='service_provider.full_name', read_only = True)
    location  = serializers.CharField(source='service_provider.address', read_only = True)
    subcategory = serializers.CharField(source='service.subcategory', read_only=True)
    description = serializers.CharField(source='service.description', read_only=True)
    customer_address = serializers.CharField(source='customer.address', read_only=True)
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequest
        fields = [
            'booking_id', 'location','serviceprovider', 'subcategory', 'description', 
            'acceptance_status', 'availability_from', 'availability_to', 'image', 
            'profile_image', 'customer_address'
        ]
    
    def get_profile_image(self, obj):
        # Access the profile image through the ServiceRegister's service_provider field
        return obj.service.service_provider.profile_image.url if obj.service.service_provider.profile_image else None
    
    def update(self, instance, validated_data):
        # Update the instance with the validated data
        instance.acceptance_status = validated_data.get('acceptance_status', instance.acceptance_status)
        instance.save()
        return instance


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'invoice_type', 'service_request', 'sender', 
            'receiver', 'quantity', 'price', 'total_amount', 'payment_status',
            'invoice_date', 'due_date', 'appointment_date', 'additional_requirements',
            'accepted_terms'
        ]
        read_only_fields = ['invoice_number', 'total_amount']
    
    def create(self, validated_data):
        # Extract the service_request to update its work_status later
        service_request = validated_data.get('service_request')

        # Create the invoice instance
        invoice = Invoice.objects.create(**validated_data)

        # Update the work_status of the associated service request
        if service_request:
            if service_request.acceptance_status == 'accept':
                service_request.work_status = 'in_progress'  # Set the desired work_status
                service_request.save()

        return invoice