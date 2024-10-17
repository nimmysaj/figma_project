from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, OTP, ServiceRequest, ServiceRegister, User, Subcategory, Invoice
from .serializers import UserRegistrationSerializer, OTPVerifySerializer, ServiceRequestSerializer, ServiceRequestDetailSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

"""

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Save user and retrieve the user object
            return Response({'message': 'User registered successfully. OTP sent to the provided contact method.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def post(self, request, *args, **kwargs):
        # Only pass the OTP code to the serializer
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            # Optionally delete OTP after successful verification
            otp_code = request.data.get('otp_code')
            otp_instance = OTP.objects.filter(otp_code=otp_code).latest('created_at')
            otp_instance.delete()  # Delete or mark as used
            return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""



#For register new request
class ServiceRequestCreateView(generics.CreateAPIView):
    serializer_class = ServiceRequestSerializer
    permission_classes = [AllowAny]

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
                service=service_register,  # Store the full ServiceRegister instance (ID)
                work_status='pending',
                acceptance_status='pending',
                availability_from=request.data.get('availability_from'),
                availability_to=request.data.get('availability_to'),
                additional_notes=request.data.get('additional_notes'),
                image=request.data.get('image'),
                title=request.data.get('title'),
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

    def put(self, request, *args, **kwargs):
        try:
            user_id = request.data.get('user_id')
            service_request_id = request.data.get('service_request_id')

            # Validate the user and service request ID
            customer = User.objects.get(id=user_id)
            service_request = ServiceRequest.objects.get(id=service_request_id, customer=customer)

            # Ensure acceptance_status is 'accept' before allowing the update
            if service_request.acceptance_status != 'accept':
                return Response({"error": "Cannot reschedule. The service request must be accepted."}, 
                                status=status.HTTP_400_BAD_REQUEST)

            # Update fields for rescheduling
            service_request.availability_from = request.data.get('availability_from', service_request.availability_from)
            service_request.availability_to = request.data.get('availability_to', service_request.availability_to)
            service_request.additional_notes = request.data.get('additional_notes', service_request.additional_notes)
            service_request.title = request.data.get('title', service_request.title)
            if 'image' in request.data:
                service_request.image = request.data.get('image')

            # If any of the fields changed, set reschedule_status to True
            #if (
             #   service_request.availability_from != request.data.get('availability_from') or
              #  service_request.availability_to != request.data.get('availability_to') 
            #):
            service_request.reschedule_status = True

            service_request.save()

            # Fetch related data in one query using select_related
            service_request = ServiceRequest.objects.select_related(
                'customer', 'service_provider', 'service'
            ).get(id=service_request.id)

            # Serialize and return updated data
            serializer = self.get_serializer(service_request)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except ServiceRequest.DoesNotExist:
            return Response({"error": "Service request not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



#For the second page , The customer can view all the services that requested
class ServiceRequestDetailView(APIView):
    permission_classes = [AllowAny]
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
                #'title': service_request.service.title,
                'title': service_request.service.title,
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

