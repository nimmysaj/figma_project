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
from .serializers import ServiceProviderLoginSerializer,PaymentListSerializer,CustomerReviewSerializer
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