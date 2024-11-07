import re
from phonenumbers import NumberParseException, is_valid_number, parse
import phonenumbers
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import serializers,status
from django.contrib.auth import authenticate
from app1.models import Complaint, CustomerReview, DeclineServiceModel, Invoice, Payment, ServiceProvider, ServiceRegister, ServiceRequest, Subcategory, User, CurrentLocation
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
    
    def validate_new_password(self, value):
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

        # Update customer fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle User fields separately
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # Save the customer instance with updated data
        instance.save()
        return instance
    

'''
#service registration and view the registered services of themselves
class ServiceRegisterSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.title', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.title', read_only=True)
    amount_paid = serializers.IntegerField(source='subcategory.collar.amount', read_only=True)
    available_lead_balance = serializers.SerializerMethodField( read_only=True)

    class Meta:
        model = ServiceRegister
        fields = [
            'id', 'description', 'gstcode', 'category', 'category_name',
            'subcategory', 'subcategory_name', 'license', 'image',
            'status', 'accepted_terms', 'available_lead_balance', 'amount_paid',
        ]

    def validate(self, data):
        # Validate that terms are accepted
        accepted_terms = data.get('accepted_terms')
        if not accepted_terms:
            raise serializers.ValidationError("You must accept the terms and conditions to register a service.")
        
        # Ensure that the service provider will be assigned from the view, not directly through input data.
        return data
    
    def get_available_lead_balance(self, obj):
        # Check service type and calculate lead balance accordingly
        if obj.subcategory and obj.subcategory.service_type.name == 'Daily Work':
            return 0  # Daily Work services don't have a lead balance
        elif obj.subcategory and obj.subcategory.service_type.name == 'One Time Lead':
            return obj.available_lead_balance or obj.subcategory.collar.lead_quantity
        return None
    
    def create(self, validated_data):
        # Remove fields not in the actual model
        validated_data.pop('available_lead_balance', None)
        validated_data.pop('amount_paid', None)

        # Create the service register instance
        service_register = super().create(validated_data)

        # Set and save the available lead balance for 'One Time Lead'
        if service_register.subcategory.service_type.name == 'One Time Lead':
            service_register.available_lead_balance = service_register.subcategory.collar.lead_quantity
            service_register.save(update_fields=['available_lead_balance'])


        # Create the corresponding invoice automatically
        self.create_invoice(service_register)

        return service_register

    def create_invoice(self, service_register):
        """
        Creates an invoice for the registered service based on the collar amount.
        """
        # Find the admin user who will be the receiver of the payment
        admin_user = User.objects.filter(is_superuser=True).first()
        
        # Use the collar amount associated with the subcategory for the invoice
        collar_amount = service_register.subcategory.collar.amount

        if collar_amount:
            Invoice.objects.create(
                invoice_type='service_registration',  # Assuming this represents a service-related invoice
                sender=service_register.service_provider.user,  # Service provider as sender
                receiver=admin_user,  # Admin as receiver
                price=collar_amount,
                total_amount=collar_amount,
                accepted_terms=service_register.accepted_terms
            )
'''
class ServiceRegisterSerializer(serializers.ModelSerializer):
    #available_lead_balance = serializers.SerializerMethodField(read_only=True)
    collar_amount = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ServiceRegister
        fields = [
            'id', 'description', 'gstcode', 'category', 'subcategory', 'license', 'status',
             'image', 'accepted_terms', 'available_lead_balance', 'collar_amount'
        ]
        read_only_fields = ['available_lead_balance', 'collar_amount','status']
    
    def get_available_lead_balance(self, obj):
        # Check if the subcategory exists and is of 'One Time Lead' type
        if obj.subcategory and obj.subcategory.service_type.name == 'One Time Lead':
            # Check if there's an associated collar for the subcategory
            if obj.subcategory.collar:
                # Get the available lead balance from the collar table
                return obj.subcategory.collar.lead_quantity or 0  # Return 0 if lead balance is None
            return 0  # Return 0 if collar is missing.
        
        # If the service type is 'Daily Work', the lead balance should always be 0
        if obj.subcategory and obj.subcategory.service_type.name == 'Daily Work':
            return 0

        # Return None for other cases or if subcategory is missing
        return None
    
    def get_collar_amount(self, obj):
        if obj.subcategory.service_type.name == 'Daily Work':
            return obj.subcategory.collar.amount
        elif obj.subcategory.service_type.name == 'One Time Lead' and obj.subcategory.collar:
            return obj.subcategory.collar.amount
        return None

    def create(self, validated_data):
        service_provider = self.context['service_provider']
        #validated_data.pop('available_lead_balance', None)
        validated_data.pop('collar_amount', None)

        # Calculate the available lead balance based on the subcategory
        subcategory = validated_data.get('subcategory')
        if subcategory and subcategory.service_type.name == 'One Time Lead' and subcategory.collar:
            validated_data['available_lead_balance'] = subcategory.collar.lead_quantity

        service_register = ServiceRegister.objects.create(
            service_provider=service_provider, **validated_data
        )
        self.create_invoice(service_register)

        return service_register

    def create_invoice(self, service_register):
        collar_amount = self.get_collar_amount(service_register)

        # Find the admin user who will be the receiver of the payment
        admin_user = User.objects.filter(is_superuser=True).first()

        if collar_amount:
            Invoice.objects.create(
                invoice_type='service_registration',
                service_register=service_register,
                sender=service_register.service_provider.user,
                receiver=admin_user,  # Admin as receiver
                price=collar_amount,
                total_amount=collar_amount,
                payment_balance=collar_amount,
                accepted_terms=service_register.accepted_terms
            )

#update service register and lead balance
class ServiceRegisterUpdateSerializer(serializers.ModelSerializer):
    add_lead = serializers.IntegerField(required=False)

    class Meta:
        model = ServiceRegister
        fields = ['description', 'gstcode', 'status', 'accepted_terms', 'add_lead']

    def update(self, instance, validated_data):
        # Ensure only active services can be updated
        if instance.status != 'Active':
            raise serializers.ValidationError({"message": "Only active services can be updated."})

        # Process lead addition if provided
        add_lead = validated_data.pop('add_lead', None)
        collar_amount = instance.subcategory.collar.amount  # Fetch collar amount

        # Update fields excluding category and subcategory
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if add_lead is not None:
            # Check for unlimited leads on Daily Work type
            if instance.subcategory.service_type.name == "Daily Work":
                raise serializers.ValidationError({
                    "message": "You have unlimited leads. No need to add or adjust lead balance."
                })

            # Calculate the lead quantity and total amount for this addition
            lead_quantity = instance.subcategory.collar.lead_quantity * add_lead
            amount_to_paid = collar_amount * add_lead
            self.context['total_lead_quantity'] = lead_quantity
            self.context['amount_to_paid'] = amount_to_paid

            # Create a draft invoice for the lead addition
            self.create_invoice(instance, amount_to_paid, collar_amount, add_lead)

        instance.save()
        return instance

    def create_invoice(self, instance, amount_to_paid, collar_amount, add_lead):
        """
        Creates an invoice for the added leads as a draft for payment.
        """
        admin_user = User.objects.filter(is_superuser=True).first()
        if amount_to_paid > 0:
            Invoice.objects.create(
                service_register=instance,  # Ensure this references the correct ServiceRegister instance
                invoice_type='lead_purchase',
                sender=instance.service_provider.user,  # Service provider as the sender
                receiver=admin_user,
                quantity=add_lead,
                price=collar_amount,
                total_amount=amount_to_paid,
                payment_balance=amount_to_paid,
                accepted_terms=instance.accepted_terms,
                payment_status='pending'  # Initially set as pending until paid
            )



#service request
class ServiceRequestSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    subcategory = serializers.CharField(source='service.subcategory', read_only=True)
    service_type = serializers.CharField(source='service.subcategory.service_type', read_only=True)
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'booking_id', 'customer_name','title', 'subcategory', 'service_type', 'acceptance_status', 'request_date', 
            'availability_from', 'availability_to','image','reschedule_status'
        ]


class CustomerServiceRequestSerializer(serializers.ModelSerializer):
    serviceprovider = serializers.CharField(source='service_provider.full_name', read_only = True)
    location  = serializers.CharField(source='service_provider.district', read_only = True)
    subcategory = serializers.CharField(source='service.subcategory', read_only=True)
    description = serializers.CharField(source='service.description', read_only=True)
    customer_address = serializers.CharField(source='customer.district', read_only=True)
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
        service_type_name = instance.service.subcategory.service_type.name

        # If the service type is "Daily work", update the acceptance status
        if service_type_name == "Daily Work":
            instance.acceptance_status = validated_data.get(
                'acceptance_status', instance.acceptance_status)
            if instance.acceptance_status == "accept":
                instance.save()  # Save only if the service is accepted
            return instance  # Return the updated instance

        # If the service type is "One time lead", return customer details
        elif service_type_name == "One time lead":
            customer = instance.customer  # Get the customer related to the service request
            # Return customer details as a structured response
            customer_details = {
                "full_name": customer.full_name,
                "address": customer.address,
                "landmark": customer.landmark,
                "pincode": customer.pin_code,
                "phone": customer.phone_number,
                "email": customer.email,
            }
            return customer_details  # Return customer details as the response
        # Raise validation error if the service type is neither "Daily work" nor "One time lead"
        else:
            raise serializers.ValidationError(
                "service type cannot access.")



class InvoiceSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # Ensure total_amount is read-only
    payment_status = serializers.CharField(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'invoice_type', 'service_request', 'sender', 
            'receiver', 'quantity', 'price', 'total_amount','payment_balance', 'payment_status',
            'invoice_date', 'due_date', 'appointment_date', 'additional_requirements',
            'accepted_terms'
        ]
        read_only_fields = ['invoice_number', 'total_amount', 'payment_balance']
    
    def validate(self, data):
        """
        Ensure that both the appointment_date and due_date are in the future,
        and the due_date is greater than or equal to the appointment_date.
        """
        appointment_date = data.get('appointment_date')
        due_date = data.get('due_date')

        current_time = timezone.now().replace(second=0, microsecond=0)

        # Validate that appointment_date is in the future
        if appointment_date and appointment_date < current_time:
            raise serializers.ValidationError(
                "The appointment date must be in the future.")

        # Validate that due_date is in the future
        if due_date and due_date < current_time:
            raise serializers.ValidationError(
                "The due date must be in the future.")

        # Validate th
        # at due_date is greater than or equal to appointment_date
        if appointment_date and due_date and due_date < appointment_date:
            raise serializers.ValidationError(
                "The due date must be greater than or equal to the appointment date.")

        return data
    
    def create(self, validated_data):
        quantity = validated_data.get('quantity')
        price = validated_data.get('price')

        # Calculate total amount
        total_amount = quantity * price if quantity and price else 0.0
        validated_data['total_amount'] = total_amount
        validated_data['payment_balance'] = total_amount


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


class ServiceDetailsSerializer(serializers.ModelSerializer):
    serviceprovider = serializers.CharField(
        source='service_provider.full_name', read_only=True)
    # service_title = serializers.CharField(source='service.title')
    location = serializers.CharField(
        source='service_provider.address', read_only=True)
    service_description = serializers.CharField(
        source='service.description', read_only=True)
    customer_address = serializers.CharField(
        source='customer.address', read_only=True)
    profile_image = serializers.SerializerMethodField()
    availability_from = serializers.DateTimeField(read_only=True)
    availability_to = serializers.DateTimeField(read_only=True)

    invoice_number = serializers.CharField(
        source='invoices.first.invoice_number', read_only=True)
    invoice_quantity = serializers.IntegerField(
        source='invoices.first.quantity', read_only=True)
    invoice_price = serializers.DecimalField(
        source='invoices.first.price', max_digits=10, decimal_places=2, read_only=True)
    invoice_total = serializers.DecimalField(
        source='invoices.first.total_amount', max_digits=10, decimal_places=2, read_only=True)
    invoice_accepted_terms = serializers.BooleanField(
        source='invoices.first.accepted_terms', read_only=True)
    additional_requirements = serializers.CharField(
        source='invoices.first.additional_requirements', read_only=True)
    appointment_date = serializers.DateTimeField(
        source='invoices.first.appointment_date', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'serviceprovider', 'location', 'customer_address', 'profile_image',
            'availability_from', 'availability_to', 'service_description', 'invoice_number',
            'invoice_quantity', 'invoice_price', 'invoice_total', 'invoice_accepted_terms',
            'appointment_date', 'additional_requirements', 'booking_id', 'image'
        ]

    def get_profile_image(self, obj):
        # Access the profile image through the ServiceRegister's service_provider field
        return obj.service.service_provider.profile_image.url if obj.service.service_provider.profile_image else None


class DeclineServiceRequestSerializer(serializers.ModelSerializer):
    images = serializers.ImageField(max_length=None, use_url=True, required=False, allow_null=True)
    decline_reason = serializers.CharField(max_length=255)

    class Meta:
        model = DeclineServiceModel
        fields = ['decline_reason', 'images', 'service_requests']

    def create(self, validated_data):
        # Create the DeclineServiceModel instance with the validated data
        decline_service = DeclineServiceModel.objects.create(**validated_data)
        
        # Update the related ServiceRequest's status fields
        service_request = decline_service.service_requests
        service_request.acceptance_status = "decline"
        service_request.work_status = "cancelled"
        service_request.save()

        return decline_service

#active services    
class ServiceRequestCustomSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name')
    service_provider_name = serializers.CharField(source='service_provider.full_name')

    rating_value = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequest
        fields = ['booking_id', 'title', 'service', 'work_status', 'request_date', 'availability_from', 'availability_to', 'customer_name', 'service_provider_name', 'rating_value']

    def get_rating_value(self, obj):
        review = CustomerReview.objects.filter(service_request=obj).first()
        if review:
            return review.rating
        return None  


#service provider complaint
class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            'id', 'sender', 'receiver', 'service_request', 'subject',
            'description', 'images', 'submitted_at', 'status', 
            'resolved_at', 'resolution_notes'
        ]
        read_only_fields = ['sender', 'receiver', 'submitted_at', 'status', 'resolved_at', 'resolution_notes']



class PaymentListSerializer(serializers.ModelSerializer): 
    invoice_type = serializers.CharField(source='invoice.invoice_type', read_only=True) 
    class Meta: 
        model = Payment 
        fields = ['transaction_id', 'sender', 'receiver', 'invoice_type', 'payment_status']

class CustomerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerReview
        fields = ['id', 'rating', 'image', 'comment', 'created_at', 'customer', 'service_provider','service_request']    



class SimpleServiceRequestSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name')  # Assuming there is a customer name field
    title = serializers.CharField()  # Assuming 'title' is a field in ServiceRequest
    request_date = serializers.DateTimeField()  # Assuming 'request_date' is a field in ServiceRequest

    class Meta:
        model = ServiceRequest
        fields = ['customer_name', 'title', 'request_date']


class UpdateLocationSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    country = serializers.CharField(max_length=100, required=False)
    state = serializers.CharField(max_length=100, required=False)
    place = serializers.CharField(max_length=100, required=False)
    address = serializers.CharField(required=False)
    landmark = serializers.CharField(max_length=100, required=False)
    pincode = serializers.CharField(max_length=20, required=False)

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise ValidationError("Longitude must be between -180 and 180.")
        return value