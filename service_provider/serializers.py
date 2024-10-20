import re
from phonenumbers import NumberParseException, is_valid_number, parse
import phonenumbers
from rest_framework.response import Response
from rest_framework import serializers,status
from django.contrib.auth import authenticate
from Accounts.models import Invoice, ServiceProvider, ServiceRegister, ServiceRequest, Subcategory, User, Payment  
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError

#service provider login
class ServiceProviderLoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        password = attrs.get('password')

        if not email_or_phone:
            raise serializers.ValidationError('Email or phone is required.')
        if not password:
            raise serializers.ValidationError('Password is required.')

        user = authenticate(username=email_or_phone, password=password)
        if user is None:
            try:
                user = User.objects.get(phone_number=email_or_phone)  
                if not user.check_password(password):
                    user = None
            except User.DoesNotExist:
                user = None

        if user is None:
            raise serializers.ValidationError('Invalid login credentials.')

        attrs['user'] = user
        return attrs


#forgot password and reset password
class ServiceProviderPasswordForgotSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True)

    def validate_email_or_phone(self, value):
        """
        This function will check if the provided value is either a valid email or a phone number.
        For now, we assume the input is either an email or phone number.
        """
        if '@' in value:
            # Validate as email
            if not User.objects.filter(email=value, is_service_provider=True).exists():
                raise serializers.ValidationError("This email is not registered with any service provider.")
        else:
            # Validate as phone number
            if not User.objects.filter(phone_number=value, is_service_provider=True).exists():
                raise serializers.ValidationError("This phone number is not registered with any service provider.")

        return value    

class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate_password(self, value):
        # Use Django's password validators to validate the password
        validate_password(value)

        # Custom validation for password complexity
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs


#profile updation
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 
            'full_name',
            'address', 
            'landmark',
            'pin_code',
            'district',
            'state',
            'watsapp',
            'email',
            'country_code',
            'phone_number'
            ]
        
class ServiceProviderSerializer(serializers.ModelSerializer):
    user = UserSerializer()

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
            "accepted_terms" 
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
    


#service registration and view the registered services of themselves
class ServiceRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRegister
        fields = ['id', 'service_provider', 'description', 'gstcode', 'category', 'subcategory', 'license', 'image', 'status', 'accepted_terms', 'available_lead_balance']

    def validate(self, data):
        service_provider = data.get('service_provider')
        # Ensure service provider is active and approved
        # Check if the service provider is approved by the dealer
        if service_provider.verification_by_dealer != 'APPROVED':
            raise serializers.ValidationError("Service provider must be approved by the dealer to register the service.")
        if service_provider.status != 'Active':
            raise serializers.ValidationError("Service provider must be active to register the service.")

        return data

#update service register and lead balance
class ServiceRegisterUpdateSerializer(serializers.ModelSerializer):
    add_lead = serializers.IntegerField(required=False)
   
    class Meta:
        model = ServiceRegister
        fields = ['description', 'gstcode', 'status', 'accepted_terms', 'add_lead']

    def update(self, instance, validated_data):
        add_lead = validated_data.pop('add_lead', None)

        # Update fields excluding category and subcategory
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Fetch the lead quantity from the SubCategory model
        if instance.subcategory and instance.subcategory.collar:
            lead_quantity = instance.subcategory.collar.lead_quantity  # Adjust field name as necessary
            print(lead_quantity)

            # Fetch the amount from the Collar model
            if instance.subcategory.collar:  # Assuming `collar` is a field in ServiceRegister
                collar_amount = instance.subcategory.collar.amount  # Adjust field name as necessary
                print(collar_amount)

                # Check if the service type is "Daily Work"
                if instance.subcategory.service_type.name == "Daily Work" and add_lead is not None:
                 # If it's "Daily Work", respond with a message without modifying the lead balance.
                    raise serializers.ValidationError({"message": "You have unlimited leads. No need to add or adjust lead balance."})
                
                if add_lead is not None:# Fetch the lead quantity from the subcategory and collar
                    if instance.subcategory and instance.subcategory.collar:
                        lead_quantity = instance.subcategory.collar.lead_quantity  # Adjust the field names as necessary
                        # Update the available lead balance by multiplying the lead quantity
                        total_lead_quantity = lead_quantity * add_lead
                        instance.available_lead_balance += total_lead_quantity
                        amount_to_paid = collar_amount * add_lead
                        print(amount_to_paid)
                        self.context['total_lead_quantity'] = total_lead_quantity           
                        self.context['amount_to_paid'] = amount_to_paid
                            
                else:
                    instance.available_lead_balance
 
        instance.save()
        return instance
    
#service request
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
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # Ensure total_amount is read-only

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
        quantity = validated_data.get('quantity')
        price = validated_data.get('price')

        # Calculate total amount
        total_amount = quantity * price if quantity and price else 0.0
        validated_data['total_amount'] = total_amount


        # Extract the service_request to update its work_status later
        service_request = validated_data.get('service_request')

        # Create the invoice instance
        invoice = Invoice.objects.create(**validated_data)

        # Update the work_status of the associated service request
        if service_request:
            if service_request.acceptance_status == 'accept':
                service_request.work_status = 'pending'  # Set the desired work_status
                service_request.save()

        return invoice


class PaymentListSerializer(serializers.ModelSerializer): 
    invoice_type = serializers.CharField(source='invoice.invoice_type', read_only=True) 
    class Meta: 
        model = Payment 
        # fields = ['transaction_id', 'sender', 'receiver', 'amount_paid', 'payment_method', 'payment_status', 'payment_date'] 
        fields = ['transaction_id', 'sender', 'receiver', 'invoice_type', 'payment_status']