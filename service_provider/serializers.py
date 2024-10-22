from rest_framework import serializers
from Accounts.models import (
    ServiceRequest,
    User,
    Invoice,
    Payment,
    DeclineServiceModel,
    ServiceRegister, Service_Type
)
from django.contrib.auth import authenticate
from django.utils import timezone


# class ServiceRegisterSerializer(serializers.ModelSerializer):

#     available_lead_balance = serializers.SerializerMethodField(read_only=True)
#     collar_amount = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = ServiceRegister
#         fields = ['id', 'service_provider', 'description', 'gstcode', 'category', 'subcategory', 'license',
#                   'status', 'image', 'accepted_terms', 'available_lead_balance', 'collar_amount']
#         read_only_fields = ['available_lead_balance', 'collar_amount']


#     def get_available_lead_balance(self, obj):
#         if obj.subcategory and obj.subcategory.service_type.name == 'Daily Work':
#             return 0  # For 'Daily Work', the lead balance is always 0.
#         elif obj.subcategory and obj.subcategory.service_type.name == 'One Time Lead':
#             if obj.subcategory.collar:
#                 # If available_lead_balance is None, return the collar's lead balance, else return the saved balance.
#                 return obj.update_lead_balance(1)
#             return 0  # Return 0 if collar is missing.
#         return None

#     def get_collar_amount(self, obj):
#         if obj.subcategory.service_type.name == 'Daily Work':
#             return obj.subcategory.collar.amount
#         elif obj.subcategory.service_type.name == 'One Time Lead' and obj.subcategory.collar:
#             return obj.subcategory.collar.amount
#         return None

#     def create(self, validated_data):
#         # Remove fields not in the actual model
#         validated_data.pop('available_lead_balance', None)
#         validated_data.pop('collar_amount', None)

#         # Create the service register instance
#         service_register = super().create(validated_data)

#         # Create the corresponding invoice automatically
#         self.create_invoice(service_register)

#         return service_register

#     def create_invoice(self, service_register):
#         """
#         Creates an invoice for the registered service based on the collar amount.
#         """
#         collar_amount = self.get_collar_amount(service_register)
#         if collar_amount:
#             Invoice.objects.create(
#                 invoice_type='service_register',  # Assuming service-related invoice
#                 sender=service_register.service_provider.user,  # Assuming service provider is the sender
#                 receiver=service_register.service_provider.dealer.user,  # Assuming dealer is the receiver
#                 price=collar_amount,
#                 total_amount=collar_amount,
#                 accepted_terms=service_register.accepted_terms
#             )
#     def validate(self, data):
#         service_provider = data.get('service_provider')
#         # Ensure service provider is active and approved
#         # Check if the service provider is approved by the dealer
#         if service_provider.verification_by_dealer != 'APPROVED':
#             raise serializers.ValidationError("Service provider must be approved by the dealer to register the service.")
#         if service_provider.status != 'Active':
#             raise serializers.ValidationError("Service provider must be active to register the service.")

#         return data


# update service register and lead balance
# class ServiceRegisterUpdateSerializer(serializers.ModelSerializer):
#     add_lead = serializers.IntegerField(required=False)

#     class Meta:
#         model = ServiceRegister
#         fields = ['description', 'gstcode', 'status', 'accepted_terms', 'add_lead']

#     def update(self, instance, validated_data):
#         add_lead = validated_data.pop('add_lead', None)

#         # Update fields excluding category and subcategory
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         # Fetch the lead quantity from the SubCategory model
#         if instance.subcategory and instance.subcategory.collar:
#             lead_quantity = instance.subcategory.collar.lead_quantity  # Adjust field name as necessary
#             print(lead_quantity)

#             # Fetch the amount from the Collar model
#             if instance.subcategory.collar:  # Assuming `collar` is a field in ServiceRegister
#                 collar_amount = instance.subcategory.collar.amount  # Adjust field name as necessary
#                 print(collar_amount)

#                 # Check if the service type is "Daily Work"
#                 if instance.subcategory.service_type.name == "Daily Work" and add_lead is not None:
#                  # If it's "Daily Work", respond with a message without modifying the lead balance.
#                     raise serializers.ValidationError({"message": "You have unlimited leads. No need to add or adjust lead balance."})

#                 if add_lead is not None:# Fetch the lead quantity from the subcategory and collar
#                     if instance.subcategory and instance.subcategory.collar:
#                         lead_quantity = instance.subcategory.collar.lead_quantity  # Adjust the field names as necessary
#                         # Update the available lead balance by multiplying the lead quantity
#                         total_lead_quantity = lead_quantity * add_lead
#                         instance.available_lead_balance += total_lead_quantity
#                         amount_to_paid = collar_amount * add_lead
#                         print(amount_to_paid)
#                         self.context['total_lead_quantity'] = total_lead_quantity
#                         self.context['amount_to_paid'] = amount_to_paid
#                         self.create_invoice(instance, amount_to_paid)


#                 else:
#                     instance.available_lead_balance

#         instance.save()
#         return instance
#     def create_invoice(self, service_register, amount_to_paid):
#         """
#         Creates an invoice for the registered service based on the calculated amount to be paid.
#         """
#         # Fetch the collar amount based on the provided service_register
#         Invoice.objects.create(
#             invoice_type='service_register',  # Assuming this is for a service registration
#             sender=service_register.service_provider.user,  # Service provider as sender
#             receiver=service_register.service_provider.dealer.user,  # Dealer as receiver
#             price=amount_to_paid,
#             total_amount=amount_to_paid,
#             accepted_terms=service_register.accepted_terms
#         )

# service request

class ServiceRequestSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source='customer.full_name', read_only=True)
    subcategory = serializers.CharField(
        source='service.subcategory', read_only=True)
    service_type = serializers.CharField(
        source='service.subcategory.service_type', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'title', 'customer_name', 'subcategory', 'acceptance_status',
            'request_date', 'availability_from', 'availability_to', 'image', 'service_type'
        ]


# class ServiceProviderLoginSerializer(serializers.Serializer):
#     email_or_phone = serializers.CharField()
#     password = serializers.CharField()

#     def validate(self, attrs):
#         email_or_phone = attrs.get('email_or_phone')
#         password = attrs.get('password')

#         if not email_or_phone:
#             raise serializers.ValidationError('Email or phone is required.')
#         if not password:
#             raise serializers.ValidationError('Password is required.')

#         # Authenticate using the custom backend

#         user = authenticate(username=email_or_phone, password=password)

#         if user is None:
#             raise serializers.ValidationError('Invalid login credentials.')

#         attrs['user'] = user
#         return attrs


class CustomerServiceRequestSerializer(serializers.ModelSerializer):
    serviceprovider = serializers.CharField(
        source='service_provider.full_name', read_only=True)
    location = serializers.CharField(
        source='service_provider.address', read_only=True)
    subcategory = serializers.CharField(
        source='service.subcategory', read_only=True)
    description = serializers.CharField(
        source='service.description', read_only=True)
    customer_address = serializers.CharField(
        source='customer.address', read_only=True)
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequest
        fields = [
            'booking_id', 'location', 'serviceprovider', 'subcategory', 'description',
            'acceptance_status', 'availability_from', 'availability_to', 'image',
            'profile_image', 'customer_address'
        ]

    def get_profile_image(self, obj):
        return obj.service.service_provider.profile_image.url if obj.service.service_provider.profile_image else None

    def update(self, instance, validated_data):
        service_type_name = instance.service.subcategory.service_type.name

        # If the service type is "Daily work", update the acceptance status
        if service_type_name == "Daily work":
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
                "Only 'Daily work' can be accepted.")


class InvoiceSerializer(serializers.ModelSerializer):
    payment_status = serializers.CharField(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'invoice_type', 'service_request', 'sender',
            'receiver', 'quantity', 'price', 'total_amount', 'payment_status',
            'invoice_date', 'due_date', 'appointment_date', 'additional_requirements',
            'accepted_terms'
        ]
        read_only_fields = ['invoice_number', 'total_amount']

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

        # Validate that due_date is greater than or equal to appointment_date
        if appointment_date and due_date and due_date < appointment_date:
            raise serializers.ValidationError(
                "The due date must be greater than or equal to the appointment date.")

        return data

    def create(self, validated_data):
        # Extract the service_request to update its work_status later
        service_request = validated_data.get('service_request')

        # Create the invoice instance
        invoice = Invoice.objects.create(**validated_data)

        return invoice


class BookingSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source='customer.full_name', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'title',
            'work_status', 'availability_from', 'availability_to',
            'rescheduled', "customer_name"
        ]


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
    images = serializers.ImageField(max_length=None, use_url=True)
    decline_reason = serializers.CharField(max_length=255)

    class Meta:
        model = DeclineServiceModel
        fields = ['decline_reason', 'images', 'service_requests']

    def create(self, validated_data):
        # Create the DeclineServiceModel instance with the validated data
        decline_service = DeclineServiceModel.objects.create(**validated_data)
        return decline_service
    #     fields = ['image', 'decline_reason']

    # def create(self, validated_data):
    #     # Pop the image field if it is present in the data
    #     image = validated_data.pop('image', None)
    #     # Create the DeclineServiceModel instance with the rest of the validated data
    #     decline_service = DeclineServiceModel.objects.create(**validated_data)

    #     # Handle the image field if it was passed
    #     if image:
    #         decline_service.image = image
    #         decline_service.save()

    #     return decline_service


# class ServiceRegisterUpdateSerializer(serializers.ModelSerializer):
#     add_lead = serializers.IntegerField(required=False)

#     class Meta:
#         model = ServiceRegister
#         fields = ['description', 'gstcode', 'status', 'accepted_terms', 'add_lead']

#     def update(self, instance, validated_data):
#         add_lead = validated_data.pop('add_lead', None)

#         # Update fields excluding category and subcategory
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         # Fetch the lead quantity from the SubCategory model
#         if instance.subcategory and instance.subcategory.collar:
#             lead_quantity = instance.subcategory.collar.lead_quantity  # Adjust field name as necessary
#             print(lead_quantity)

#             # Fetch the amount from the Collar model
#             if instance.subcategory.collar:  # Assuming `collar` is a field in ServiceRegister
#                 collar_amount = instance.subcategory.collar.amount  # Adjust field name as necessary
#                 print(collar_amount)

#                 # Check if the service type is "Daily Work"
#                 if instance.subcategory.service_type.name == "Daily Work" and add_lead is not None:
#                  # If it's "Daily Work", respond with a message without modifying the lead balance.
#                     raise serializers.ValidationError({"message": "You have unlimited leads. No need to add or adjust lead balance."})

#                 if add_lead is not None:# Fetch the lead quantity from the subcategory and collar
#                     if instance.subcategory and instance.subcategory.collar:
#                         lead_quantity = instance.subcategory.collar.lead_quantity  # Adjust the field names as necessary
#                         # Update the available lead balance by multiplying the lead quantity
#                         total_lead_quantity = lead_quantity * add_lead
#                         instance.available_lead_balance += total_lead_quantity
#                         amount_to_paid = collar_amount * add_lead
#                         print(amount_to_paid)
#                         self.context['total_lead_quantity'] = total_lead_quantity
#                         self.context['amount_to_paid'] = amount_to_paid

#                 else:
#                     instance.available_lead_balance

#         instance.save()
#         return instance
