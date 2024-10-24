from django.shortcuts import get_object_or_404
import phonenumbers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from customer.permissions import IsOwnerOrAdmin
from figma import settings
from .utils import send_otp_via_email, send_otp_via_phone
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import smart_bytes
from .serializers import CustomerLoginSerializer,CustomerPasswordForgotSerializer, CustomerSerializer, ResendOTPSerializer, ServiceProviderProfileSerializer,ServiceProviderSerializer,RegisterSerializer, ServiceRequestDetailSerializer, ServiceRequestSerializer,SetNewPasswordSerializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.pagination import PageNumberPagination
from Accounts.models import OTP, Category, Country_Codes, Customer, Invoice, ServiceProvider, ServiceRegister, ServiceRequest, Subcategory, User
from rest_framework import status, permissions,generics,viewsets,serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login
from django.core.mail import send_mail
from .serializers import CategorySerializer,SubcategorySerializer
from rest_framework.decorators import action
from rest_framework.throttling import UserRateThrottle


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Send OTP via email or phone
            if user.email:
                send_otp_via_email(user)
            elif user.phone_number:
                send_otp_via_phone(user)

            return Response({'message': 'User registered successfully. Please verify OTP to complete registration.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyOTPView(APIView):
    def post(self, request):
        otp_code = request.data.get('otp_code')
        email_or_phone = request.data.get('email_or_phone')

        if not otp_code or not email_or_phone:
            return Response({"detail": "OTP code and email/phone number are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Find user by either email or phone number
        user = None
        if '@' in email_or_phone:
            user = User.objects.filter(email=email_or_phone).first()
        else:
            try:
                fullnumber=phonenumbers.parse(email_or_phone,None)
                code=Country_Codes.objects.get(calling_code="+"+str(fullnumber.country_code))
                number=str(fullnumber.national_number)
            except phonenumbers.phonenumberutil.NumberParseException:
                raise serializers.ValidationError('Wrong phone number or email format')
            user = User.objects.filter(phone_number=number,country_code=code).first()
            
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check OTP
        try:
            otp = OTP.objects.filter(user=user).latest('created_at')
        except OTP.DoesNotExist:
            return Response({"detail": "OTP not found."}, status=status.HTTP_404_NOT_FOUND)

        if otp.is_expired():
            return Response({"detail": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)

        if otp.otp_code != otp_code:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
       
        # Activate user
        user.is_active = True
        user.save()

        # Delete OTP after successful verification
        otp.delete()

        return Response({"detail": "OTP verified. Account activated."}, status=status.HTTP_200_OK)

class OTPResendThrottle(UserRateThrottle):
    rate = '3/hour'  # Allows 3 requests per hour

class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    serializer_class = ResendOTPSerializer
    throttle_classes = [OTPResendThrottle]

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.get_user()

            # Resend OTP via email or phone
            if user.email:
                send_otp_via_email(user)
            elif user.phone_number:
                send_otp_via_phone(user)

            return Response({'message': 'OTP resent successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CustomerLoginView(APIView):
    def post(self, request):
        serializer = CustomerLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if user.is_customer:
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            update_last_login(None, user)  # Update last login timestamp

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'User is not a customer.'}, status=status.HTTP_403_FORBIDDEN)


class SetNewPasswordView(generics.UpdateAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request, *args, **kwargs):
        user = request.user  # Get the authenticated user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set the new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'detail': 'Password has been updated successfully.'}, status=status.HTTP_200_OK)


class CustomerPasswordForgotView(generics.GenericAPIView):
    serializer_class = CustomerPasswordForgotSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Validate the input (email or phone)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data['email_or_phone']

        # Determine if it's an email or phone and find the user
        if '@' in email_or_phone:
            user = User.objects.get(email=email_or_phone, is_customer=True)
        else:
            #user = User.objects.get(phone_number=email_or_phone, is_customer=True)
            try:
                fullnumber=phonenumbers.parse(email_or_phone,None)
                code=Country_Codes.objects.get(calling_code="+"+str(fullnumber.country_code))
                number=str(fullnumber.national_number)
                user = User.objects.get(phone_number=number,country_code=code)
            except phonenumbers.phonenumberutil.NumberParseException:
                raise serializers.ValidationError('Wrong phone number or email format')    

        # Generate the password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(smart_bytes(user.pk))

        # Generate the reset link
        reset_link = f"http://127.0.0.1:8000/customer/password-reset/{uid}/{token}/"

        # Send an email if an email was provided
        if '@' in email_or_phone:
            send_mail(
                'Password Reset Request',
                f"Use the following link to reset your password: {reset_link}",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            print(reset_link)
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


class CustomerViewSet(viewsets.ModelViewSet):
    permission_class =[IsAuthenticated,IsOwnerOrAdmin]
    queryset =Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_queryset(self):
        # Admins see all, service providers see only their own profiles
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Customer.objects.all()
        
        # Non-admins can only see their own profile
        return Customer.objects.filter(user=self.request.user)

# List all active categories
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(status='Active')
    serializer_class = CategorySerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]  # Override JWT authentication
    permission_classes = []  # This removes any permission restrictions

# List all active subcategories under a specific category
class SubcategoryListView(generics.ListAPIView):
    serializer_class = SubcategorySerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]  # Override JWT authentication
    permission_classes = []  # This removes any permission restrictions

    def get_queryset(self):
        category_id = self.kwargs['category_id']  # Get the category from URL
        return Subcategory.objects.filter(category_id=category_id, status='Active')

# List all active and verified service providers under a specific subcategory
class ServiceProviderListView(generics.ListAPIView):
    serializer_class = ServiceProviderSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]  # Override JWT authentication
    permission_classes = []  # This removes any permission restrictions

    def get_queryset(self):
        subcategory_id = self.kwargs['subcategory_id']  # Get the subcategory from URL

        # Retrieve the service providers based on the ServiceRegister model
        return ServiceProvider.objects.filter(
            services__subcategory_id=subcategory_id,  # Filter by subcategory
            services__status='Active',  # Ensure service is active
            status='Active',  # Ensure service provider is active
            verification_by_dealer='APPROVED'  # Ensure service provider is verified
        ).distinct()
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['subcategory_id'] = self.kwargs['subcategory_id']  # Pass subcategory_id to serializer context
        return context
    
#detailed view of service provider profile    
class ServiceProviderDetailView(generics.RetrieveAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]  # Override JWT authentication
    permission_classes = []  # This removes any permission restrictions
    queryset = ServiceProvider.objects.filter(status='Active', verification_by_dealer='APPROVED')  # Only active and approved providers
    serializer_class = ServiceProviderProfileSerializer
    lookup_field = 'id'  # By default, it looks up by 'id', you can change it if using a custom field

    def get_queryset(self):
        # Optionally, add further filtering (e.g., subcategory-specific filtering, etc.)
        return super().get_queryset()
        

#search functionality with pagination
class CustomPagination(PageNumberPagination):
    page_size = 10  # Set the number of results per page
    page_size_query_param = 'page_size'
    max_page_size = 100  # Optionally, set a max page size if needed

class UnifiedSearchView(APIView):
    permission_classes = [AllowAny]  # No authentication required
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('search', '')
        if not query:
            return Response({"message": "Search query is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in Categories
        category_results = Category.objects.filter(status='Active', title__icontains=query)
        category_serializer = CategorySerializer(category_results, many=True)

        # Search in Subcategories
        subcategory_results = Subcategory.objects.filter(status='Active', title__icontains=query)
        subcategory_serializer = SubcategorySerializer(subcategory_results, many=True)


        # Search in Service Providers by user full_name and related subcategory title
        service_provider_by_name = ServiceProvider.objects.filter(
            status='Active',
            verification_by_dealer='APPROVED',
            user__full_name__icontains=query  # Adjust this based on your user model field
        )

        service_provider_by_subcategory = ServiceProvider.objects.filter(
            services__subcategory__title__icontains=query,  # Use `title` for subcategories
            status='Active',
            verification_by_dealer='APPROVED'
        )

       
        # Combine the two querysets manually and ensure uniqueness
        service_provider_results = (service_provider_by_name | service_provider_by_subcategory).distinct()
        service_provider_serializer = ServiceProviderSerializer(
            service_provider_results, 
            many=True, 
            context={'subcategory_id': request.query_params.get('subcategory_id')}
        )
        
        # Paginate the results
        paginator = CustomPagination()
        paginated_service_providers = paginator.paginate_queryset(service_provider_results, request)
        service_provider_serializer = ServiceProviderSerializer(
            paginated_service_providers, 
            many=True, 
            context={'subcategory_id': request.query_params.get('subcategory_id')}
        )


        # Combine all results into a single response
        response_data = {
            "categories": category_serializer.data,
            "subcategories": subcategory_serializer.data,
            "service_providers": service_provider_serializer.data
        }

        #return Response(response_data, status=status.HTTP_200_OK)
        return paginator.get_paginated_response(response_data)



#For register new request
class ServiceRequestCreateView(generics.CreateAPIView):
    serializer_class = ServiceRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Get the necessary fields from request data
            user_id = request.data.get('user_id')
            service_register_id = request.data.get('service')  # This is the ServiceRegister ID

            # Get the customer
            customer = User.objects.get(id=user_id) if user_id else None
            if not customer:
                return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Get the service based on service_register_id
            service_register = ServiceRegister.objects.get(id=service_register_id) if service_register_id else None
            if not service_register:
                return Response({"error": "Service not found for this ID."}, status=status.HTTP_404_NOT_FOUND)

            # Check if a request for the same service by the same user already exists
            existing_service_request = ServiceRequest.objects.filter(
                customer=customer,
                service=service_register
            ).exists()

            if existing_service_request:
                return Response({"error": "You already have a pending request for this service."}, status=status.HTTP_400_BAD_REQUEST)


            # Get the service provider
            service_provider_id = request.data.get('service_provider_id')
            service_provider = User.objects.get(id=service_provider_id) if service_provider_id else None
            if not service_provider:
                return Response({"error": "service_provider_id is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Create the service request (storing the ForeignKey to ServiceRegister)
            service_request = ServiceRequest.objects.create(
                customer=customer,
                service_provider=service_provider,
                title=request.data.get('title'),
                service=service_register,  # Store the full ServiceRegister instance (ID)
                work_status='pending',
                acceptance_status='pending',
                availability_from=request.data.get('availability_from'),
                availability_to=request.data.get('availability_to'),
                additional_notes=request.data.get('additional_notes'),
                image=request.data.get('image'),
                booking_id=self.generate_booking_id(),
            )

            # Fetch related data in one query using select_related()
            service_request = ServiceRequest.objects.select_related(
                'customer', 'service_provider', 'service'
            ).get(id=service_request.id)

            serializer = self.get_serializer(service_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except ServiceRegister.DoesNotExist:
            return Response({"error": "ServiceRegister not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def generate_booking_id(self):
        import uuid
        return str(uuid.uuid4())


#For the second page , The customer can view all the services that requested
class ServiceRequestDetailView(APIView):
    permission_classes = [AllowAny,IsAuthenticated]
    serializer_class = ServiceRequestDetailSerializer  # Use the new serializer

    def post(self, request, *args, **kwargs):
        try:
            # Get user_id from the request body
            user_id = request.data.get('user_id')

            # Validate if user_id is provided
            if not user_id:
                return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch all service requests made by this user
            service_requests = ServiceRequest.objects.filter(customer__id=user_id)

            # Check if there are any service requests
            if not service_requests.exists():
                return Response({"error": "No service requests found for this user."}, status=status.HTTP_404_NOT_FOUND)

            # Prepare the response data
            response_data = []
            for service_request in service_requests:
                # Serialize the basic fields
                serializer = self.serializer_class(service_request)
                service_request_data = serializer.data

                # Check if the acceptance_status is "accept"
                if service_request.acceptance_status == 'accept':
                    # Get the related invoice
                    invoice = Invoice.objects.filter(service_request=service_request).first()

                    # If an invoice exists, add the total_amount (as 'amount') to the response data
                    if invoice:
                        service_request_data['amount'] = invoice.total_amount

                # Add the service request data to the response
                response_data.append(service_request_data)

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#for view the request details that accepted and also view the pending requests
class ServiceRequestInvoiceDetailView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        service_request_id = request.data.get('service_request_id')


        service_request = get_object_or_404(ServiceRequest, id=service_request_id, customer_id=user_id)


        data = {
            'service_request': {
                'title':service_request.title,
                'service': service_request.service.subcategory.title,
                'work_status': service_request.work_status,
                'request_date': service_request.request_date,
                'availability_from': service_request.availability_from,
                'availability_to': service_request.availability_to,
                'additional_notes': service_request.additional_notes,
                'image': service_request.image.url if service_request.image else None,
                'booking_id': service_request.booking_id,
            }
        }

        # If the acceptance status is 'accept', add the invoice data
        if service_request.acceptance_status == 'accept':
            invoice = Invoice.objects.filter(service_request=service_request).first()
            if invoice:
                # Add the invoice data to the response
                data['invoice'] = {
                    'invoice_ID': invoice.invoice_number,
                    'appointment_date': invoice.appointment_date,
                    'quantity': invoice.quantity,
                    'price': invoice.price,
                    'total_amount': invoice.total_amount,
                    'additional_requirements': invoice.additional_requirements,
                    'payment_status': invoice.payment_status,
                }
            else:
                return Response({'error': 'Invoice not found for the given service request.'}, status=status.HTTP_404_NOT_FOUND)


        return Response(data, status=status.HTTP_200_OK)
