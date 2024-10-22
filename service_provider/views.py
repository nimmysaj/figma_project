from django.shortcuts import get_object_or_404, render
from django.db.models import Avg
from rest_framework.views import APIView
from django.contrib.auth import authenticate
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
from Accounts.models import ServiceProvider, ServiceRegister, ServiceRequest, User,Payment,CustomerReview
from service_provider.permissions import IsOwnerOrAdmin
from .serializers import CustomerServiceRequestSerializer, InvoiceSerializer, ServiceProviderPasswordForgotSerializer, ServiceRegisterSerializer, ServiceRegisterUpdateSerializer, ServiceRequestSerializer, SetNewPasswordSerializer, ServiceProviderLoginSerializer,ServiceProviderSerializer,PaymentListSerializer,CustomerReviewSerializer
from django.utils.encoding import smart_bytes, smart_str
from twilio.rest import Client
from rest_framework.decorators import action
from copy import deepcopy
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

    def get_queryset(self):
        # Admins see all, service providers see only their own profiles
        if self.request.user.is_staff or self.request.user.is_superuser:
            return ServiceProvider.objects.all()
        
        # Non-admins can only see their own profile
        return ServiceProvider.objects.filter(user=self.request.user)


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
            # Find the service provider associated with the authenticated user
            service_provider = ServiceProvider.objects.get(user=request.user)
            print(f"ServiceProvider ID: {service_provider.id}")

            # Check if a service with the same details already exists for this provider
            existing_service = ServiceRegister.objects.filter(
                service_provider=service_provider,
                # Add any other fields that uniquely identify a service, for example:
                category=request.data.get('category'),
                subcategory=request.data.get('subcategory')
            ).exists()

            if existing_service:
                return Response(
                    {"message": "This service is already registered by the service provider."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Check if accepted_terms is True
            accepted_terms = request.data.get('accepted_terms', False)
            if not accepted_terms:
                return Response(
                    {"message": "You must accept the terms and conditions."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # If no existing service is found, proceed with creation
            serializer = ServiceRegisterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(service_provider=service_provider)
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
            serializer.save()  # This will call the update method in the serializer
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

        # Check if the logged-in user is the service provider for the request
        if service_request.service_provider != self.request.user:
            return Response(
                {"error": "You are not authorized to create an invoice for this request."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        if service_request.invoices.exists():  # Assuming related_name='invoices' is set in Invoice model
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

        if invoice_data['accepted_terms']:
            invoice_data['service_request'] = service_request.id  # Ensure the invoice is tied to this service request
            invoice_data['sender'] = request.user.id  # The service provider is the sender
            invoice_data['receiver'] = service_request.customer.id  # The customer is the receiver
        

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

class PaymentListView(APIView):
    # Ensure the user is authenticated
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get the logged-in service provider's ID
        service_provider_id = request.user.id

        # Payments where the logged-in service provider is the sender (Ads)
        ads_payments = Payment.objects.filter(
            invoice__invoice_type='Ads',
            sender_id=service_provider_id
        )

        # Payments where the logged-in service provider is the receiver (Salary)
        salary_payments = Payment.objects.filter(
            invoice__invoice_type='salary',
            receiver_id=service_provider_id
        )

        # Combine both querysets
        all_payments = ads_payments | salary_payments

        # Serialize the combined payments
        serializer = PaymentListSerializer(all_payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    




class ServiceProviderReviews(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        # Get the service provider based on the user ID
        service_provider = get_object_or_404(User, id=id)

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