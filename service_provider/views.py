from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.exceptions import NotFound
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics,viewsets
from app1.models import Complaint, CustomerReview, Invoice, Payment, ServiceProvider, ServiceRegister, ServiceRequest, User, CurrentLocation
from service_provider.permissions import IsOwnerOrAdmin
from .serializers import ComplaintSerializer, CustomerReviewSerializer, CustomerServiceRequestSerializer, DeclineServiceRequestSerializer, InvoiceSerializer, PaymentListSerializer, ServiceDetailsSerializer, ServiceProviderPasswordForgotSerializer, ServiceRegisterSerializer, ServiceRegisterUpdateSerializer, ServiceRequestCustomSerializer, ServiceRequestSerializer, SetNewPasswordSerializer, ServiceProviderLoginSerializer,ServiceProviderSerializer,SimpleServiceRequestSerializer, UpdateLocationSerializer
from django.utils.encoding import smart_bytes, smart_str
from twilio.rest import Client
from django.db.models import Avg,Sum
from rest_framework.decorators import action
from copy import deepcopy
from decimal import Decimal
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
from geopy.distance import geodesic

# Create your views here.

#service provider login
class ServiceProviderLoginView(APIView):
    def post(self, request):
        serializer = ServiceProviderLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data['email_or_phone']
        password = serializer.validated_data['password']

        # Check if input is email or phone
        user = User.objects.filter(email=email_or_phone).first() or \
               User.objects.filter(phone_number=email_or_phone).first()

        if user and user.check_password(password):
            if user.is_service_provider:
                # Create JWT token
                refresh = RefreshToken.for_user(user)
                update_last_login(None, user)  # Update last login time

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'User is not a service provider.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

#set new password
class SetNewPasswordView(generics.UpdateAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [permissions.IsAuthenticated,]  # Ensure the user is authenticated
    
    
    def post(self, request, *args, **kwargs):
        user = request.user  # Get the authenticated user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set the new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'detail': 'Password has been updated successfully.'}, status=status.HTTP_200_OK)

#forgot password
class ServiceProviderPasswordForgotView(generics.GenericAPIView):
    serializer_class = ServiceProviderPasswordForgotSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Validate the input (email or phone)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data['email_or_phone']

        # Determine if it's an email or phone and find the user
        if '@' in email_or_phone:
            user = User.objects.get(email=email_or_phone, is_service_provider=True)
        else:
            user = User.objects.get(phone_number=email_or_phone, is_service_provider=True)

        # Generate the password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(smart_bytes(user.pk))

        # Generate the reset link
        reset_link = f"http://127.0.0.1:8000/service-provider/password-reset/{uid}/{token}/"

        # Send an email if an email was provided
        if '@' in email_or_phone:
            send_mail(
                'Password Reset Request',
                f"Use the following link to reset your password: {reset_link}",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return Response({'details': 'Password reset link has been sent to your email.'}, status=status.HTTP_200_OK)
        else:
            # For testing purposes, we are not sending an SMS yet, but this is where SMS logic would go
            # For example, you would use Twilio to send the SMS:
        #     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        #     message = client.messages.create(
        #     from_=settings.TWILIO_PHONE_NUMBER,
        #     body=f"{reset_link}",
        #     to=user.phone_number,
        #     )
        #     print(message.sid)
            print(reset_link)
            return Response({'details': 'Password reset link has been sent to your phone.'}, status=status.HTTP_200_OK)

#reset password
class ResetPasswordView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'details': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
        return Response({'details': 'Invalid token or User ID'}, status=status.HTTP_400_BAD_REQUEST)
    

#profile updation of service providers
class ServiceProviderViewSet(viewsets.ModelViewSet):
    permission_class =[IsAuthenticated, IsOwnerOrAdmin]
    queryset =ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    lookup_field = 'user'  # Use 'user' instead of 'pk'

    def get_queryset(self):
        # Admins see all, service providers see only their own profiles
        if self.request.user.is_staff or self.request.user.is_superuser:
            return ServiceProvider.objects.all()
        
        # Non-admins can only see their own profile
        return ServiceProvider.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        # Retrieve the customer profile for the authenticated user
        serviceprovider = self.get_queryset().first()
        if not serviceprovider:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(serviceprovider)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        # Update the customer profile for the authenticated user
        serviceprovider = self.get_queryset().first()
        if not serviceprovider:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(serviceprovider, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        # Allows PATCH requests to update parts of the profile
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


#service registration,update,lead balance
class ServiceRegisterViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access

    def list(self, request):
        try:
            # Find the ServiceProvider instance for the authenticated user
            service_provider = ServiceProvider.objects.get(user=request.user)

            # Filter services based on the service provider's ID
            queryset = ServiceRegister.objects.filter(service_provider=service_provider.id)

            if not queryset.exists():
                return Response(
                    {"message": "No services found for this provider."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Serialize the data
            serializer = ServiceRegisterSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error for debugging
            print(f"Error fetching services: {e}")
            return Response(
                {"error": "An error occurred while retrieving services."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(ServiceRegister, pk=pk)
        serializer = ServiceRegisterSerializer(instance)
        return Response(serializer.data)

    def create(self, request):
        try:
            # Fetch the service provider instance for the authenticated user directly from the token
            service_provider = ServiceProvider.objects.get(user=request.user)
            
            # Ensure that the service provider is approved and active before allowing service registration
            if service_provider.verification_by_dealer != 'APPROVED' or service_provider.status != 'Active':
                return Response(
                    {"error": "Service provider must be active and approved to register a service."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if accepted_terms is True
            accepted_terms = request.data.get('accepted_terms', False)
            if not accepted_terms:
                return Response({"message": "You must accept the terms and conditions."},
                                status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if a service with the same details already exists for this provider
            existing_service = ServiceRegister.objects.filter(
                service_provider=service_provider,
                category=request.data.get('category'),
                subcategory=request.data.get('subcategory')
            ).exists()

            if existing_service:
                return Response(
                    {"message": "This service is already registered by the service provider."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            

            # Serialize the data with the service provider included in the context
            serializer = ServiceRegisterSerializer(data=request.data, context={'service_provider': service_provider})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ServiceProvider.DoesNotExist:
            return Response(
                {"error": "ServiceProvider not found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            print(f"Error during service registration: {str(e)}")
            return Response(
                {"error": "An error occurred while registering the service.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
    def update(self, request, pk=None):
        # Retrieve the ServiceRegister instance or return a 404
        instance = get_object_or_404(ServiceRegister, pk=pk)

        # Check if `accepted_terms` is set to True
        accepted_terms = request.data.get('accepted_terms', False)
        if not accepted_terms:
            return Response(
                {"message": "You must accept the terms and conditions."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use the serializer to validate and partially update the instance
        serializer = ServiceRegisterUpdateSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            # Save updated data
            serializer.save()

            return Response({
                "message": "Service updated successfully.",
                "data": serializer.data,
                "available_lead_balance": instance.available_lead_balance,
                "added_lead": serializer.context.get('total_lead_quantity'),
                "amount_to_paid": serializer.context.get('amount_to_paid'),
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Failed to update service.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        

'''            
    def update(self, request, pk=None):
        # Retrieve the instance or return a 404 error
        instance = get_object_or_404(ServiceRegister, pk=pk)

        # Check if accepted_terms is True
        accepted_terms = request.data.get('accepted_terms', False)
        if not accepted_terms:
            return Response(
                {"message": "You must accept the terms and conditions."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the instance using the serializer
        serializer = ServiceRegisterUpdateSerializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            instance.save()  # Save the updated instance
            return Response({
                "message": "Service updated successfully.",
                "data": serializer.data,
                "available_lead_balance": instance.available_lead_balance,
                "added_lead": serializer.context.get('total_lead_quantity'),
                "amount_to_paid": serializer.context.get('amount_to_paid'),
                }, status=status.HTTP_200_OK)


        return Response({
            "message": "Failed to update service.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
'''

#service request view
class ServiceProviderRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Fetch the logged-in user's ServiceProvider instance
            service_provider = ServiceProvider.objects.get(user=request.user)
            # Filter service requests assigned to the logged-in service provider
            service_requests = ServiceRequest.objects.filter(service_provider=request.user)
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

    def get(self, request, pk, *args, **kwargs):
        try:
            # Ensure the logged-in user is a service provider
            service_provider = ServiceProvider.objects.get(user=request.user)
            # Get the service request by ID (pk) and ensure it belongs to the logged-in service provider
            service_request = ServiceRequest.objects.get(pk=pk, service_provider=service_provider.user)
        except ServiceRequest.DoesNotExist:
            return Response({"error": "Service request not found or access denied."}, status=404)
        except ServiceProvider.DoesNotExist:
            return Response({"error": "Service provider not found."}, status=404)

        # Serialize the service request details
        serializer = CustomerServiceRequestSerializer(service_request)
        return Response(serializer.data, status=200)

    def post(self, request, pk, *args, **kwargs):
        try:
            # Ensure the logged-in user is a service provider
            service_provider = ServiceProvider.objects.get(user=request.user)
            # Get the service request by ID (pk) and ensure it belongs to the logged-in service provider
            service_request = ServiceRequest.objects.get(pk=pk, service_provider=service_provider.user)
        except ServiceRequest.DoesNotExist:
            return Response({"error": "Service request not found or access denied."}, status=404)
        except ServiceProvider.DoesNotExist:
            return Response({"error": "Service provider not found."}, status=404)

        # Serialize and update the work_status
        serializer = CustomerServiceRequestSerializer(service_request, data=request.data, partial=True)

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

    def get(self, request, pk, *args, **kwargs):
        try:
            # Ensure the logged-in user is a service provider
            service_provider = ServiceProvider.objects.get(user=self.request.user)
            # Get the service request by ID (pk) and ensure it belongs to the logged-in service provider
            service_request = ServiceRequest.objects.get(pk=pk, service_provider=service_provider.user)
        except ServiceRequest.DoesNotExist:
            return Response({"error": "Service request not found or access denied."}, status=404)
        except ServiceProvider.DoesNotExist:
            return Response({"error": "Service provider not found."}, status=404)

        # Serialize the service request details
        serializer = CustomerServiceRequestSerializer(service_request)
        response_data = serializer.data
        response_data['work_status'] = service_request.work_status
        return Response(response_data, status=200)

    def post(self, request, pk, *args, **kwargs):
            # Fetch the service request for which the invoice is being created
            service_request = get_object_or_404(ServiceRequest, pk=pk)
            print(service_request.service.subcategory.service_type)
            if service_request.service.subcategory.service_type != 'One Time Lead':
                # Check if the logged-in user is the service provider for the request
                if service_request.service_provider != self.request.user:
                    return Response(
                        {"error": "You are not authorized to create an invoice for this request."}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                
                if service_request.servicerequests_invoices.exists():  # Assuming related_name='invoices' is set in Invoice model
                    return Response({
                        "error": "An invoice has already been created for this service request."
                    }, status=status.HTTP_400_BAD_REQUEST)

                if service_request.acceptance_status == 'pending':
                    return Response({
                        "error": "Cannot generate invoice. Request acceptance is pending."
                    }, status=status.HTTP_400_BAD_REQUEST)

                elif service_request.acceptance_status == 'decline':
                    return Response({
                        "error": "Cannot generate invoice. Request has been declined."
                    }, status=status.HTTP_400_BAD_REQUEST)


                # Create a mutable copy of request.data        
                invoice_data = deepcopy(request.data)

                if not invoice_data.get('accepted_terms', False):
                    invoice_data['accepted_terms'] = True 
                # Add additional fields to invoice_data
                admin_user = User.objects.filter(is_superuser=True).first()
                if invoice_data['accepted_terms']:
                    invoice_data['service_request'] = service_request.id  # Ensure the invoice is tied to this service request
                    invoice_data['sender'] = service_request.customer.id  # The customer is the payment sender
                    invoice_data['receiver'] = admin_user.id  # The admin is the payment receiver
                    invoice_data['invoice_type'] = "service_request"
                    

                    # Serialize and save the invoice
                    invoice_serializer = InvoiceSerializer(data=invoice_data)
                    if invoice_serializer.is_valid():
                        invoice = invoice_serializer.save()  # This will call the create method in the serializer

                        if service_request.work_status != 'pending':
                            service_request.work_status = 'pending'
                            service_request.save()

                        return Response({
                            "message": "Invoice created successfully.",
                            "invoice": invoice_serializer.data,
                            "work_status": service_request.work_status
                        }, status=status.HTTP_201_CREATED)

                    # Return an error response if the invoice data is invalid
                    return Response(invoice_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(
                        {"error": "Cannot generate invoice. Accepted terms must be true."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                        {"error": "Cannot generate invoice. It's a lead work!"}, 
                        status=status.HTTP_400_BAD_REQUEST   
                ) 
            
    def patch(self, request, pk, *args, **kwargs):
        # Get the invoice instance related to the given service request ID (pk)
        try:
            service_request = get_object_or_404(ServiceRequest, pk=pk)
            if service_request.reschedule_status==True:
            
                invoice = Invoice.objects.get(service_request=service_request)

                # Ensure the logged-in user is the service provider for this request
                service_provider = ServiceProvider.objects.get(user=self.request.user)
                if service_request.service_provider != service_provider.user:
                    return Response(
                        {"error": "You are not authorized to update this invoice."},
                        status=status.HTTP_403_FORBIDDEN
                    )

                # Update the appointment_date field
                appointment_date = request.data.get('appointment_date', None)
                if not appointment_date:
                    return Response(
                        {"error": "Appointment date is required."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Update and save the appointment date
                invoice.appointment_date = appointment_date
                invoice.save()

                # Set the `reschedule_status` of the related service request to `False`
                service_request = invoice.service_request
                service_request.reschedule_status = False
                service_request.save()

                # Serialize the updated invoice data
                serializer = InvoiceSerializer(invoice)
                return Response({
                    "message": "Service resceduled successfully.",
                    "rescheduled": service_request.reschedule_status,
                    "invoice": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "message": "No request for reschduling."}
                    )


        except Invoice.DoesNotExist:
            return Response({"error": "Invoice not found for this service request."}, status=404)
        except ServiceProvider.DoesNotExist:
            return Response({"error": "Service provider not found."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    
        

#bookings and appointments      
class BookingsServiceRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Get the logged-in service provider
            service_provider = get_object_or_404(ServiceProvider, user=request.user)
            
            # Filter service requests where work_status is 'pending' and reschedule_status
            service_requests = ServiceRequest.objects.filter(
                service_provider=service_provider.user,
                work_status='pending'
            )

            # Serialize the service requests
            serializer = ServiceRequestSerializer(service_requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ServiceProvider.DoesNotExist:
            return Response({"error": "Service provider not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)  


#service detail view
class ServiceDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceDetailsSerializer

    def get_queryset(self):
        return ServiceRequest.objects.select_related('service_provider', 'service', 'customer').prefetch_related('invoices')

    def get(self, request, *args, **kwargs):
        pk = request.data.get('pk')  # Get the pk from the request body
        print(pk)
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


#decline view
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

#deduct lead
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

class ComplaintViewSet(viewsets.ModelViewSet):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]
    queryset = Complaint.objects.all()  # Define queryset for ModelViewSet compatibility

    def list(self, request, *args, **kwargs):
        """Retrieve all complaints for the logged-in customer."""
        complaints = self.queryset.filter(sender=request.user)
        
        if not complaints.exists():
            return Response({"message": "No complaints found for this customer."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(complaints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            service_request_id = request.data.get('service_request_id')
            service_request = ServiceRequest.objects.get(id=service_request_id)

            service_provider = service_request.service_provider
            service_provider_instance = ServiceProvider.objects.get(user=service_provider)
            franchise = service_provider_instance.franchisee
            franchisee_user = franchise.user

            if not franchisee_user or not isinstance(franchisee_user, User):
                return Response({"error": "Franchisee not found for the service provider."},
                                status=status.HTTP_404_NOT_FOUND)
            
            existing_complaint = Complaint.objects.filter(
                sender=request.user,
                service_request=service_request
            ).exists()

            if existing_complaint:
                return Response(
                    {"error": "A complaint for this service request has already been registered."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            complaint = Complaint.objects.create(
                sender=user,
                receiver=franchisee_user,
                service_request=service_request,
                subject=request.data.get('subject'),
                description=request.data.get('description'),
                images=request.FILES.get('images')
            )
            
            serializer = self.get_serializer(complaint)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except ServiceRequest.DoesNotExist:
            return Response({"error": "Service request not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Custom action to list active complaints
    @action(detail=False, methods=['get'], url_path='active')
    def list_active_complaints(self, request):
        active_complaints = self.queryset.filter(sender=request.user,status__in=['pending', 'in_progress'])
        serializer = self.get_serializer(active_complaints, many=True)
        return Response(serializer.data)

    # Custom action to list completed complaints
    @action(detail=False, methods=['get'], url_path='completed')
    def list_completed_complaints(self, request):
        completed_complaints = self.queryset.filter(sender=request.user,status__in=['resolved', 'rejected'])
        serializer = self.get_serializer(completed_complaints, many=True)
        return Response(serializer.data)


#Active services
class OngoingServiceRequestView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Get the logged-in service provider
            service_provider = get_object_or_404(ServiceProvider, user=request.user)
            
            # Filter service requests where work_status is 'pending' and reschedule_status
            service_requests = ServiceRequest.objects.filter(
                service_provider=service_provider.user,
                work_status='in_progress'
            )

            # Serialize the service requests
            serializer = ServiceRequestCustomSerializer(service_requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ServiceProvider.DoesNotExist:
            return Response({"error": "Service provider not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)  


class CompletedServiceRequestView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Get the logged-in service provider
            service_provider = get_object_or_404(ServiceProvider, user=request.user)
            
            # Filter service requests where work_status is 'pending' and reschedule_status
            service_requests = ServiceRequest.objects.filter(
                service_provider=service_provider.user,
                work_status='completed'
            )

            # Serialize the service requests
            serializer = ServiceRequestCustomSerializer(service_requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ServiceProvider.DoesNotExist:
            return Response({"error": "Service provider not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)  

class ServiceRequestCompleteStatus(APIView):
    def post(self, request, *args, **kwargs):
        booking_id = request.data.get('id')
        work_status = request.data.get('work_status')

        if not booking_id or not work_status:
            return Response({"error": "booking_id and work_status are required."}, status=status.HTTP_400_BAD_REQUEST)

        if work_status != 'completed':
            return Response({"error": "Only 'completed' status is allowed."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service_request = ServiceRequest.objects.get(booking_id=booking_id)
        except ServiceRequest.DoesNotExist:
            raise NotFound("Service request not found.")

        if service_request.work_status == 'completed':
            return Response({"error": "This service request is already marked as completed."}, status=status.HTTP_400_BAD_REQUEST)


        if service_request.work_status == 'in_progress':
            service_request.work_status = work_status
            service_request.save()

            # Serialize the updated service request
            serializer = ServiceRequestCustomSerializer(service_request)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"message": "The service request is not in 'in_progress' status."}, status=status.HTTP_400_BAD_REQUEST)


#transaction page
class PaymentListView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, *args, **kwargs):
        # Get the logged-in user's ID
        user_id = request.user.id

        # Filter payments where the user is either the sender or receiver
        payments = Payment.objects.filter(sender_id=user_id) | Payment.objects.filter(receiver_id=user_id)

        # Check if the user has any payments
        if not payments.exists():
            # Return a response indicating no transaction history
            return Response({
                'message': 'No transactions found for this user.'
            }, status=200)

        # If payments exist, serialize the payments
        serializer = PaymentListSerializer(payments, many=True)

        # Return the serialized data
        return Response(serializer.data, status=200)

#finance page
class FinancialOverviewView(APIView):
    # Ensure the user is authenticated
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get the logged-in service provider's ID
        user_id = request.user.id

        # Calculate expenditure (where service provider is the sender)
        expenditure = Payment.objects.filter(
            sender_id=user_id
        ).aggregate(total_expenditure=Sum('amount_paid'))['total_expenditure'] or 0

        # Calculate income (where service provider is the receiver)
        income = Payment.objects.filter(
            receiver_id=user_id
        ).aggregate(total_income=Sum('amount_paid'))['total_income'] or 0

        # Return the financial summary
        data = {
            'income': income,
            'expenditure': expenditure
        }

        return Response(data, status=status.HTTP_200_OK)


#reviews page
class ServiceProviderReviews(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the service provider based on the user ID
        user_id = request.user.id
        service_provider = get_object_or_404(User, id=user_id)

        # Fetch reviews related to this service provider
        reviews = CustomerReview.objects.filter(service_provider=service_provider)

        # Calculate the average rating
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        total_reviews = reviews.count()


        if average_rating < 1:
            rating_scale = "Poor"
        elif average_rating < 2:
            rating_scale = "Fair"
        elif average_rating < 3:
            rating_scale = "Good"
        elif average_rating < 4:
            rating_scale = "Very Good"
        else:
            rating_scale = "Excellent"


        serializer = CustomerReviewSerializer(reviews, many=True)


        return Response({
            'reviews': serializer.data,
            'average_rating': average_rating,
            'total_reviews': total_reviews,
            'rating_scale': rating_scale  
        })


class ServiceProviderCountsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get the logged-in service provider
        service_provider = get_object_or_404(ServiceProvider, user=request.user)

        # Count of registered services
        registered_services_count = ServiceRegister.objects.filter(service_provider=service_provider).count()

        # Count of active jobs
        active_jobs_count = ServiceRequest.objects.filter(
            service_provider=request.user,
            work_status='in_progress'
        ).count()

        # Count of service requests
        service_requests_count = ServiceRequest.objects.filter(service_provider=request.user).count()

        #completed jobs count 
        completed_jobs_count = ServiceRequest.objects.filter(
            service_provider = service_provider.user,
            work_status = 'completed'
        ).count()

        # Return counts in response
        return Response({
            "Registered Services": registered_services_count,
            "Active jobs": active_jobs_count,
            "Service Requests": service_requests_count,
            "Complete Jobs": completed_jobs_count,
        }, status=200)


class ServiceProviderDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get the logged-in service provider
        service_provider = get_object_or_404(ServiceProvider, user=request.user)

        # Define the time filter
        one_day_ago = timezone.now() - timedelta(days=1)

        # Recent Activities (updated in the last 24 hours)
        recent_activities = ServiceRequest.objects.filter(
            service_provider=request.user,
            updated_at__gte=one_day_ago
        ).values('booking_id', 'title', 'work_status', 'updated_at')

        # Active services (in progress and updated within the last 24 hours)
        active_services = ServiceRequest.objects.filter(
            service_provider=request.user,
            work_status="in_progress",
            updated_at__gte=one_day_ago
        )
        active_services_serializer = SimpleServiceRequestSerializer(active_services, many=True)

        # Active bookings (pending or rescheduled, updated within the last 24 hours)
        active_bookings = ServiceRequest.objects.filter(
            service_provider=service_provider.user,
            updated_at__gte=one_day_ago
        ).filter(
            Q(work_status='pending') | Q(reschedule_status=True)
        )
        active_bookings_serializer = SimpleServiceRequestSerializer(active_bookings, many=True)

        # Service requests (all requests updated within the last 24 hours)
        service_requests = ServiceRequest.objects.filter(
            service_provider=request.user,
            acceptance_status = "pending",
            updated_at__gte=one_day_ago
        )
        service_requests_serializer = SimpleServiceRequestSerializer(service_requests, many=True)

        # Return detailed information
        return Response({
            "Recent Activities": recent_activities,
            "Active Services Details(In progress)": active_services_serializer.data,
            "Bookings(work status  - pending & reschedualed)": active_bookings_serializer.data,
            "Requests(Accept status - Pending)": service_requests_serializer.data,
        }, status=200)



class ServiceProviderRevenueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get the logged-in service provider
        service_provider = get_object_or_404(ServiceProvider, user=request.user)

        # Calculate total revenue from all paid invoices received by the provider
        total_revenue = Invoice.objects.filter(
            receiver=request.user,
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

        # Count the number of paid services
        no_of_paid_services = Invoice.objects.filter(
            receiver=request.user,
            payment_status="paid"
        ).count()

        # Initialize revenue breakdown data
        services_revenue_data = []
        services_revenue_data.append({
            'No of paid services': no_of_paid_services,
        })

        # Get unique paid services
        paid_services = Invoice.objects.filter(
            receiver=request.user,
            payment_status='paid'
        ).values('service_register').distinct()

        for entry in paid_services:
            service_id = entry['service_register']
            service = ServiceRegister.objects.get(id=service_id)
            
            # Calculate revenue for each service
            service_revenue = Invoice.objects.filter(
                receiver=request.user,
                service_register=service,
                payment_status='paid'
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

            # Calculate the revenue percentage for each service
            revenue_percentage = (
                (service_revenue / total_revenue * 100) if total_revenue > 0 else 0
            )

            # Count the number of times the service has been bought
            service_purchase_count = Invoice.objects.filter(
                receiver=request.user,
                service_register=service,
                payment_status='paid'
            ).count()

            # Append service data with revenue, percentage, and purchase count
            services_revenue_data.append({
                'service_name': service.subcategory.title,
                'amount_paid': float(service_revenue),
                'revenue_percentage': float(revenue_percentage),
                'times_bought': service_purchase_count,
            })

        # Return the revenue breakdown in the response
        return Response({
            "Total Revenue": float(total_revenue),
            "Services Revenue Breakdown": services_revenue_data,
        }, status=200)


class ServiceReachView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service_provider = get_object_or_404(User, full_name=request.user.full_name)
        provider_start_date = service_provider.created_at.strftime('%Y-%m')

        # Fetch and count service requests by month
        monthly_request_counts = (
            ServiceRequest.objects.filter(service_provider=service_provider)
            .annotate(month=TruncMonth('request_date'))
            .values('month')
            .annotate(request_count=Count('id'))
            .order_by('month')
        )

        # Format the data to show counts per month
        request_dates = {entry['month'].strftime('%Y-%m'): entry['request_count'] for entry in monthly_request_counts}

        # Prepare the response
        return Response({
            "service_requests_count": sum(request_dates.values()),
            "provider_start_date": provider_start_date,
            "request_dates": request_dates,  # Dictionary with month as key and request count as value
        })
    



class UpdateLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get latitude and longitude from the request data
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        # Validate if latitude and longitude are provided
        if latitude is None or longitude is None:
            return Response({"error": "Latitude and longitude are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate latitude and longitude data type and range in one step
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            if not (-90 <= latitude <= 90):
                return Response({"error": "Latitude must be between -90 and 90."}, status=status.HTTP_400_BAD_REQUEST)
            if not (-180 <= longitude <= 180):
                return Response({"error": "Longitude must be between -180 and 180."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Latitude and longitude must be valid decimal numbers."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch or create the provider's current location record
        location, created = CurrentLocation.objects.get_or_create(user=request.user)
        
        # Update location fields
        location.latitude = latitude
        location.longitude = longitude
        
        # Optionally update other fields if they are provided
        location.country = request.data.get("country", location.country)
        location.state = request.data.get("state", location.state)
        location.place = request.data.get("place", location.place)
        location.address = request.data.get("address", location.address)
        location.landmark = request.data.get("landmark", location.landmark)
        location.pincode = request.data.get("pincode", location.pincode)

        location.save()

        return Response({"message": "Location updated successfully."}, status=status.HTTP_200_OK)



    

class ProviderLocationDistanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract data from the request body
        provider_email = request.data.get("provider_email")  # Changed to provider_email
        customer_lat = request.data.get("customer_lat")
        customer_lon = request.data.get("customer_lon")

        # Check that required fields are present
        if not provider_email or customer_lat is None or customer_lon is None:
            return Response(
                {"error": "provider_email, customer_lat, and customer_lon are required fields"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch provider location using the email
        provider_user = get_object_or_404(User, email=provider_email)  # Fetch the user first
        provider_location = get_object_or_404(CurrentLocation, user=provider_user)  # Then fetch location using the user object

        provider_lat = provider_location.latitude
        provider_lon = provider_location.longitude

        # Validate the customer latitude and longitude
        try:
            customer_lat = float(customer_lat)
            customer_lon = float(customer_lon)
        except ValueError:
            return Response(
                {"error": "customer_lat and customer_lon must be valid numbers"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate distance between customer and provider
        provider_coords = (provider_lat, provider_lon)
        customer_coords = (customer_lat, customer_lon)
        distance_km = geodesic(customer_coords, provider_coords).km

        # Return the response
        return Response({
            "provider_latitude": provider_lat,
            "provider_longitude": provider_lon,
            "distance_km": round(distance_km, 2)
        }, status=200)