from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from copy import deepcopy
from Accounts.models import ServiceRequest, ServiceProvider, Invoice, ServiceRegister
from .serializers import (
    # ServiceProviderLoginSerializer,
    ServiceRequestSerializer,
    CustomerServiceRequestSerializer,
    InvoiceSerializer,
    BookingSerializer,
    ServiceDetailsSerializer,
    DeclineServiceRequestSerializer,
    # ServiceRegisterSerializer,
    # ServiceRegisterUpdateSerializer
)
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, generics
from Accounts.models import User
from django.contrib.auth import get_user_model
from django.db.models import Q


User = get_user_model()


# class ServiceProviderLoginView(APIView):
#     def post(self, request):
#         serializer = ServiceProviderLoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         email_or_phone = serializer.validated_data['email_or_phone']
#         password = serializer.validated_data['password']

#         # Check if input is email or phone
#         user = User.objects.filter(email=email_or_phone).first() or \
#                User.objects.filter(phone_number=email_or_phone).first()

#         if user and user.check_password(password):
#             if user.is_service_provider:
#                 # Create JWT token
#                 refresh = RefreshToken.for_user(user)
#                 update_last_login(None, user)  # Update last login time

#                 return Response({
#                     'refresh': str(refresh),
#                     'access': str(refresh.access_token),
#                 }, status=status.HTTP_200_OK)
#             else:
#                 return Response(
#                     {'detail': 'User is not a service provider.'},
#                     status=status.HTTP_403_FORBIDDEN
#                 )
#         else:
#             return Response(
#                 {'detail': 'Invalid credentials.'},
#                 status=status.HTTP_401_UNAUTHORIZED
#             )


# class ServiceRegisterViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access

#     def list(self, request):
#         try:
#             # Find the ServiceProvider instance for the authenticated user
#             service_provider = ServiceProvider.objects.get(user=request.user)

#             # Filter services based on the service provider's ID
#             queryset = ServiceRegister.objects.filter(service_provider=service_provider.id)

#             if not queryset.exists():
#                 return Response(
#                     {"message": "No services found for this provider."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )

#             # Serialize the data
#             serializer = ServiceRegisterSerializer(queryset, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         except Exception as e:
#             # Log the error for debugging
#             print(f"Error fetching services: {e}")
#             return Response(
#                 {"error": "An error occurred while retrieving services."},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#     def retrieve(self, request, pk=None):
#         instance = get_object_or_404(ServiceRegister, pk=pk)
#         serializer = ServiceRegisterSerializer(instance)
#         return Response(serializer.data)

#     def create(self, request):
#         try:
#             # Find the service provider associated with the authenticated user
#             service_provider = ServiceProvider.objects.get(user=request.user)
#             print(f"ServiceProvider ID: {service_provider.id}")

#             # Check if a service with the same details already exists for this provider
#             existing_service = ServiceRegister.objects.filter(
#                 service_provider=service_provider,
#                 # Add any other fields that uniquely identify a service, for example:
#                 category=request.data.get('category'),
#                 subcategory=request.data.get('subcategory')
#             ).exists()

#             if existing_service:
#                 return Response(
#                     {"message": "This service is already registered by the service provider."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             # Check if accepted_terms is True
#             accepted_terms = request.data.get('accepted_terms', False)
#             if not accepted_terms:
#                 return Response(
#                     {"message": "You must accept the terms and conditions."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # If no existing service is found, proceed with creation
#             serializer = ServiceRegisterSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save(service_provider=service_provider)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         except ServiceProvider.DoesNotExist:
#             return Response(
#                 {"error": "ServiceProvider not found for this user."},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             print(f"Error during service registration: {str(e)}")
#             print(e)
#             return Response(
#                 {"error": "An error occurred while registering the service.", "details": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#     def update(self, request, pk=None):
#         # Retrieve the instance or return a 404 error
#         instance = get_object_or_404(ServiceRegister, pk=pk)

#         # Check if accepted_terms is True
#         accepted_terms = request.data.get('accepted_terms', False)
#         if not accepted_terms:
#             return Response(
#                 {"message": "You must accept the terms and conditions."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Update the instance using the serializer
#         serializer = ServiceRegisterUpdateSerializer(instance, data=request.data, partial=True)

#         if serializer.is_valid():
#             serializer.save()
#             instance.save()  # Save the updated instance
#             return Response({
#                 "message": "Service updated successfully.",
#                 "data": serializer.data,
#                 "available_lead_balance": instance.available_lead_balance,
#                 "added_lead": serializer.context.get('total_lead_quantity'),
#                 "amount_to_paid": serializer.context.get('amount_to_paid'),
#                 }, status=status.HTTP_200_OK)


#         return Response({
#             "message": "Failed to update service.",
#             "errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)


class ServiceProviderRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Fetch the logged-in user's ServiceProvider instance
            service_provider = ServiceProvider.objects.get(user=request.user)
            # Filter service requests assigned to the logged-in service provider
            service_requests = ServiceRequest.objects.filter(
                service_provider=request.user)
            # Serialize the service requests
            serializer = ServiceRequestSerializer(service_requests, many=True)
            # Return the serialized data as a response
            return Response(serializer.data, status=200)

        except ServiceProvider.DoesNotExist:
            return Response({"error": "User is not a service provider."}, status=400)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)


class CustomerServiceRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Get the service request ID (pk) from the request data
            pk = request.data.get('pk')

            # Ensure the logged-in user is a service provider
            service_provider = ServiceProvider.objects.get(user=request.user)

            # Get the service request by ID (pk) and ensure it belongs to the logged-in service provider
            service_request = ServiceRequest.objects.get(
                pk=pk, service_provider=service_provider.user)
        except ServiceRequest.DoesNotExist:
            return Response({"error": "Service request not found or access denied."}, status=404)
        except ServiceProvider.DoesNotExist:
            return Response({"error": "Service provider not found."}, status=404)

        # Serialize the service request details
        serializer = CustomerServiceRequestSerializer(service_request)
        return Response(serializer.data, status=200)

    def post(self, request, *args, **kwargs):
        try:
            # Get the service request ID (pk) from the request data
            pk = request.data.get('pk')

            # Ensure the logged-in user is a service provider
            service_provider = ServiceProvider.objects.get(user=request.user)

            # Get the service request by ID (pk) and ensure it belongs to the logged-in service provider
            service_request = ServiceRequest.objects.get(
                pk=pk, service_provider=service_provider.user)
        except ServiceRequest.DoesNotExist:
            return Response({"error": "Service request not found or access denied."}, status=404)
        except ServiceProvider.DoesNotExist:
            return Response({"error": "Service provider not found."}, status=404)

        # Serialize and update the work_status
        serializer = CustomerServiceRequestSerializer(
            service_request, data=request.data, partial=True)

        if serializer.is_valid():
            result = serializer.save()  # This will call the update method in the serializer

            # If the result is a dictionary, it means the service type is "One time lead"
            # This checks if the returned result is the customer details
            if isinstance(result, dict):
                return Response(result, status=200)

            # Otherwise, it's "Daily work", and we return the regular serialized data
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)


class ServiceRequestInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Get the service request ID (pk) from the request data
            pk = request.data.get('pk')

            # Ensure the logged-in user is a service provider
            service_provider = ServiceProvider.objects.get(user=request.user)

            # Get the service request by ID (pk) and ensure it belongs to the logged-in service provider
            service_request = ServiceRequest.objects.get(
                pk=pk, service_provider=service_provider.user)
        except ServiceRequest.DoesNotExist:
            return Response({"error": "Service request not found or access denied."}, status=404)
        except ServiceProvider.DoesNotExist:
            return Response({"error": "Service provider not found."}, status=404)

        # Serialize the service request details
        serializer = CustomerServiceRequestSerializer(service_request)
        return Response(serializer.data, status=200)

    def post(self, request, *args, **kwargs):
        try:
            # Get the service request ID (pk) from the request body
            pk = request.data.get('pk')

            # Fetch the service request for which the invoice is being created
            service_request = get_object_or_404(ServiceRequest, pk=pk)

            # Ensure the logged-in user is a service provider
            service_provider = ServiceProvider.objects.get(
                user=request.user)  # Get the correct service provider

            # Check if the logged-in user is the service provider for the request
            if service_request.service_provider != service_provider:
                return Response(
                    {"error": "You are not authorized to create an invoice for this request."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Check if an invoice already exists for this service request
            if service_request.invoices.exists():
                return Response({"error": "An invoice has already been created for this service request."}, status=status.HTTP_400_BAD_REQUEST)

            if service_request.acceptance_status == 'pending':
                return Response({"error": "Cannot generate invoice. Work is pending."}, status=status.HTTP_400_BAD_REQUEST)

            elif service_request.acceptance_status == 'decline':
                return Response({"error": "Cannot generate invoice. Work has been declined."}, status=status.HTTP_400_BAD_REQUEST)

            # Create a mutable copy of request.data
            invoice_data = deepcopy(request.data)
            if not invoice_data.get('accepted_terms', False):
                invoice_data['accepted_terms'] = True

            # Add additional fields to invoice_data
            if invoice_data['accepted_terms']:
                # Ensure the invoice is tied to this service request
                invoice_data['service_request'] = service_request.id
                # The customer is the sender
                invoice_data['sender'] = service_request.customer.id

                # Get the admin user as the receiver
                admin_user = User.objects.filter(is_superuser=True).first()
                if admin_user:
                    # Admin is the receiver
                    invoice_data['receiver'] = admin_user.id
                else:
                    return Response({"error": "Admin user not found."}, status=status.HTTP_400_BAD_REQUEST)

                # Serialize and save the invoice
                invoice_serializer = InvoiceSerializer(data=invoice_data)
                if invoice_serializer.is_valid():
                    invoice = invoice_serializer.save()  # Save the invoice

                    return Response({
                        "message": "Invoice created successfully.",
                        "invoice": invoice_serializer.data
                    }, status=status.HTTP_201_CREATED)

                # Return error if validation fails
                return Response(invoice_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": "Accepted terms must be true."}, status=status.HTTP_400_BAD_REQUEST)

        except ServiceRequest.DoesNotExist:
            return Response({"error": "Service request not found."}, status=404)
        except ServiceProvider.DoesNotExist:
            return Response({"error": "Service provider not found."}, status=404)

    def put(self, request, *args, **kwargs):
        try:
            # Get the service request ID (pk) from the request body
            pk = request.data.get('pk')

            # Fetch the service request by its primary key
            service_request = ServiceRequest.objects.get(pk=pk)
            # Assuming a related name 'invoices' on the model
            invoice = service_request.invoices.first()

            if not invoice:
                return Response({"error": "No invoice found for this service request."}, status=404)

            # Check if the service request is rescheduled
            if not service_request.rescheduled:
                return Response({"error": "Invoice can only be updated when the service request is rescheduled."},
                                status=status.HTTP_400_BAD_REQUEST)

            if service_request.acceptance_status != 'accept':
                return Response({"error": "Invoice can only be updated when the service request is accepted."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Proceed to update the invoice
            invoice_serializer = InvoiceSerializer(
                invoice, data=request.data, partial=True)

            if invoice_serializer.is_valid():
                invoice_serializer.save()

                # Update the acceptance_status of the service request to 'accept'
                service_request.acceptance_status = 'accept'
                service_request.save()

                return Response({
                    "message": "Invoice updated successfully.",
                    "rescheduled": service_request.rescheduled,
                    "invoice": invoice_serializer.data,
                }, status=status.HTTP_200_OK)

            # Return error if validation fails
            return Response(invoice_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ServiceRequest.DoesNotExist:
            return Response({"error": "Service request not found."}, status=404)


class BookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Ensure the logged-in user is a service provider
            service_provider = ServiceProvider.objects.get(user=request.user)

            # Fetch all service requests for the service provider
            # Combine both conditions using Q
            service_requests = ServiceRequest.objects.filter(
                service_provider=service_provider.user
            ).filter(
                # Show requests where rescheduled is True or work_status is 'pending'
                Q(rescheduled=True) | Q(work_status='pending')
            )

        except ServiceProvider.DoesNotExist:
            return Response({"error": "Service provider not found."}, status=404)

        # Serialize the service requests details
        # Use many=True for multiple objects
        serializer = BookingSerializer(service_requests, many=True)
        return Response(serializer.data, status=200)


class ServiceDetailsView(generics.RetrieveAPIView):
    serializer_class = ServiceDetailsSerializer

    def get_queryset(self):
        return ServiceRequest.objects.select_related('service_provider', 'service', 'customer').prefetch_related('invoices')

    def get(self, request, *args, **kwargs):
        pk = request.data.get('pk')  # Get the pk from the request body

        if not pk:
            return Response({"error": "No 'pk' provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the queryset and try to get the object with the provided pk
        queryset = self.get_queryset()
        try:
            service_request = queryset.get(pk=pk)
        except ServiceRequest.DoesNotExist:
            raise NotFound(detail="Service request not found.",
                           code=status.HTTP_404_NOT_FOUND)

        # Serialize the service request and return the response
        serializer = self.get_serializer(service_request)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeclineServiceView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request, *args, **kwargs):
        try:
            # Get the service request ID from the request body
            pk = request.data.get('pk')

            # Fetch the service request by its primary key
            service_request = ServiceRequest.objects.get(pk=pk)
        except ServiceRequest.DoesNotExist:
            return Response({"detail": "No ServiceRequest matches the given query."}, status=404)

        # Check if the logged-in user is the service provider for the request
        service_provider = ServiceProvider.objects.get(user=request.user)
        if service_request.service_provider != service_provider.user:
            return Response({
                "error": "You are not authorized to decline this service request."
            }, status=status.HTTP_403_FORBIDDEN)

        # Proceed if the request exists and the logged-in user is the correct service provider
        if service_request.decline_services.exists():  # Using related_name='decline_services'
            return Response({"error": "A decline request already exists for this service request."}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare data for decline creation
        data = request.data.copy()
        # Ensure this matches the field in the model
        data['service_requests'] = service_request.id

        serializer = DeclineServiceRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Service request declined successfully.",
                "decline_service": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class OnetimeLeadView(APIView):
#     serializer_class = CustomerServiceRequestSerializer

#     def get(self, request,*args, **kwargs):
#         try:
#             # Fetch the logged-in user's ServiceProvider instance
#             pk =request.data.get('pk')
#             service_provider = ServiceProvider.objects.get(user=request.user)
#             service_request = ServiceRequest.objects.get(pk=pk, service__service_provider=service_provider)
#             service_type_name = service_request.service.subcategory.service_type.name

#             if service_type_name == 'One time lead':
#                 customer = service_request.customer
#                 service_providers = service_request.service_provider
#                 customer_details = {
#                     "service_provider_name" : service_providers.full_name,
#                     "service_provider_location" : service_providers.address,
#                     "booking_id" : service_request.booking_id,
#                     "full_name" : customer.full_name,
#                     "address" : customer.address,
#                     "pin_code" : customer.pin_code,
#                     "Landmark" : customer.landmark,
#                     "ph" : customer.phone_number,
#                     "email" : customer.email
#                 }
#                 return Response(customer_details, status=200)
#             else:
#                 return Response({"error": "Invalid service type"}, status=400)

#         except ServiceProvider.DoesNotExist:
#             return Response({"error": "User is not a service provider."}, status=400)
#         except User.DoesNotExist:
#             return Response({"error": "User not found."}, status=404)
#         except ServiceRequest.DoesNotExist:
#             return Response({"error": "Service request not found."}, status=404)


class DeductLeadBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            pk = request.data.get('pk')
            # Get the logged-in service provider
            service_provider = get_object_or_404(
                ServiceProvider, user=request.user)

            # Find the corresponding ServiceRequest based on pk and service_provider
            service_request = get_object_or_404(
                ServiceRequest, pk=pk, service__service_provider=service_provider)

            # Get the ServiceRegister object tied to the service request
            service_register = service_request.service

            # Deduct one lead from the available_lead_balance
            if service_register.available_lead_balance > 0:
                service_register.available_lead_balance -= 1
                service_register.save()

                return Response({
                    "message": "Lead balance deducted successfully.",
                    "available_lead_balance": service_register.available_lead_balance
                }, status=200)
            else:
                return Response({"error": "No lead balance available to deduct."}, status=400)

        except ServiceRequest.DoesNotExist:
            return Response({"error": "Service request not found or access denied."}, status=404)
        except ServiceProvider.DoesNotExist:
            return Response({"error": "Service provider not found."}, status=404)
