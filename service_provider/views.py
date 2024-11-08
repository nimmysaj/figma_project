from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from django.db.models import Avg,Sum
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
from Accounts.models import ServiceProvider, ServiceRequest, User,Payment,CustomerReview
from service_provider.permissions import IsOwnerOrAdmin
from .serializers import ServiceProviderLoginSerializer,PaymentListSerializer
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


class PaymentListView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request, *args, **kwargs):
        user_id = request.user.id

        payments = Payment.objects.filter(sender_id=user_id) | Payment.objects.filter(receiver_id=user_id)

        if request.user.is_service_provider:
            # Include payments specifically made by customers for the provider's service requests
            service_request_payments = Payment.objects.filter(
                invoice__invoice_type='service_request',
                invoice__service_request__service_provider_id=user_id 
            )

            payments = payments | service_request_payments  

        if not payments.exists():
            return Response({
                'message': 'No transactions found for this user.'
            }, status=200)

       
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data, status=200)
    
    

class FinancialOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        user_id = user.id

        # Retrieve service provider name and profile image
        service_provider_name = user.full_name
        try:
            service_provider = ServiceProvider.objects.get(user=user)
            service_provider_image_url = service_provider.profile_image.url if service_provider.profile_image else None
        except ServiceProvider.DoesNotExist:
            service_provider_image_url = None

        
        income = 0
        expenditure = 0
        account_balance = 0

        if user.is_service_provider:
            # Income: sum of all payments received by the service provider from the admin
            income = Payment.objects.filter(
                receiver_id=user_id,
                invoice__invoice_type='provider_payment'
            ).aggregate(total_income=Sum('amount_paid'))['total_income'] or 0

            # Expenditure: sum of all payments made by the service provider
            expenditure = Payment.objects.filter(
                sender_id=user_id
            ).aggregate(total_expenditure=Sum('amount_paid'))['total_expenditure'] or 0

            # Total customer payments to admin for services
            customer_payments_to_admin = Payment.objects.filter(
                invoice__invoice_type='service_request',
                invoice__service_request__service_provider_id=user_id,
            ).aggregate(total_customer_payments=Sum('amount_paid'))['total_customer_payments'] or 0

            # Expected earnings (90% of customer payments)
            expected_earnings = customer_payments_to_admin * Decimal('0.9')
            account_balance = expected_earnings - income

            provider_payments = Payment.objects.filter(
                receiver_id=user_id,
                invoice__invoice_type='provider_payment'
            )

            
            provider_payments_serializer = PaymentListSerializer(provider_payments, many=True)
        else:
            provider_payments_serializer = []

        data = {
            'service_provider_name': service_provider_name,
            'service_provider_image_url': service_provider_image_url,
            'income': income,
            'expenditure': expenditure,
            'account_balance': account_balance,
            'admin_to_provider_transactions': provider_payments_serializer.data
        }

        return Response(data, status=status.HTTP_200_OK)