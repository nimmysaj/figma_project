from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from Accounts.models import Franchise_Type, ServiceRequest, ServiceProvider, Franchisee
from admin_app.models import *
from rest_framework import serializers
from .serializer import *
from rest_framework import status
from rest_framework.pagination import PageNumberPagination  # Import pagination class
from django.core.paginator import Paginator
import razorpay
from django.conf import settings
from admin_app.models import Payment
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from django.utils import timezone
from datetime import timedelta

# Create your views here.
class Franchise_TypeView(APIView):
    def get(self, request):
        # Retrieve all Person objects
        fnt = Franchise_Type.objects.all()
        serializer = Franchise_Type_Serializer(fnt, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Create a new Person object
        serializer = Franchise_Type_Serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # Update an existing Person object
        try:
            fnt = Franchise_Type.objects.get(id=request.data['id'])
        except Franchise_Type.DoesNotExist:
            return Response({"error": "Franchisee type not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = Franchise_Type_Serializer(fnt, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        # Partially update an existing Person object
        try:
            fnt = Franchise_Type.objects.get(id=request.data['id'])
        except Franchise_Type.DoesNotExist:
            return Response({"error": "Franchisee not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = Franchise_Type_Serializer(fnt, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Delete a Person object
        try:
            fnt = Franchise_Type.objects.get(id=request.data['id'])
        except Franchise_Type.DoesNotExist:
            return Response({"error": "Franchisee not found"}, status=status.HTTP_404_NOT_FOUND)

        fnt.delete()
        return Response({"message": "Franchisee deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class Service_HistoryPagination(PageNumberPagination):
    page_size = 5  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow client to control size
    max_page_size = 50  # Optional: Cap the maximum page size

class Service_HistoryView(APIView):

    def get(self, request, *args, **kwargs):
        # Fetch the queryset (filter as needed)
        srqts = ServiceRequest.objects.filter(
            acceptance_status__in=['accept', 'pending']
        )

        # Initialize pagination
        paginator = Service_HistoryPagination()
        paginated_srqts = paginator.paginate_queryset(srqts, request)

        # Serialize the paginated data
        serialized_data = ServiceHistorySerializer(paginated_srqts, many=True).data

        # Calculate job counts for the summary
        total_jobs = srqts.count()
        active_jobs = srqts.filter(work_status__in=['in_progress', 'In Progress']).count()
        completed_jobs = srqts.filter(work_status__in=['completed', 'Completed']).count()

        # Structure the response format
        response_data = {
            'summary': {
                'total_jobs': total_jobs,
                'active_jobs': active_jobs,
                'completed_jobs': completed_jobs,
            },
            'service_history_details': serialized_data,
        }

        # Return paginated response
        return paginator.get_paginated_response(response_data)

#     def post(self, request, *args, **kwargs):
#         # Extract franchisee_id from the request body
#         franchisee_cust_id = request.data.get('franchisee_cust_id')

#         if not franchisee_cust_id:
#             return Response(
#                 {"error": "Franchisee ID is required."}, status=status.HTTP_400_BAD_REQUEST)

#         # Filter service providers under the given franchisee
#         service_provider_ids = ServiceProvider.objects.filter(franchisee__custom_id=franchisee_cust_id).values_list('id', flat=True)

#         # Get service requests linked to those service providers
#         srqts = ServiceRequest.objects.filter(service__service_provider_id__in=service_provider_ids)
#         fjobs = ServiceRequest.objects.filter(service__service_provider__franchisee__custom_id = franchisee_cust_id)

#         # Summary for top banner
#         total_jobs = fjobs.count()
#         active_jobs = fjobs.filter(work_status__in=['in_progress', 'In Progress']).count()
#         completed_jobs = fjobs.filter(work_status__in=['completed', 'Completed']).count()

#         # Paginate the queryset
#         paginator = PageNumberPagination()
#         paginator.page_size = 5  # 5 records per page
#         paginated_srqts = paginator.paginate_queryset(srqts, request)

#         # Serialize the paginated queryset
#         serialized_data = ServiceHistorySerializer(paginated_srqts, many=True).data

#         # Return paginated response with summary
#         return paginator.get_paginated_response({
#             'summary': {
#                 'total_jobs': total_jobs,
#                 'active_jobs': active_jobs,
#                 'completed_jobs': completed_jobs
#             },
#             'service_history_details': serialized_data
#         })

class FranchiseeDetailsView(APIView):
    # To view franchisee details based on entered franchisee custom ID
    
    def post(self, request, *args, **kwargs):
        # Extract franchisee_cust_id from the request body
        franchisee_cust_id = request.data.get('franchisee_cust_id')

        if not franchisee_cust_id:
            return Response(
                {"error": "Franchisee ID is required."},status=status.HTTP_400_BAD_REQUEST
            )

        # Query the franchisee based on the given custom_id
        franchisee = Franchisee.objects.filter(custom_id=franchisee_cust_id).first()

        if not franchisee:
            return Response(
                {"error": "Franchisee not found."},status=status.HTTP_404_NOT_FOUND
            )

        # Serialize the franchisee object
        serialized_frdata = FranchiseeDetailsSerializer(franchisee).data

        return Response(serialized_frdata, status=status.HTTP_200_OK)

class AdListView(APIView):
    """
    View to list all ads or filter based on query parameters.
    """

    def get(self, request, *args, **kwargs):
        # Optional filtering logic (e.g., filter ads by 'target_area' or date range)
        queryset = Ad_Management.objects.all()

        # Serialize the queryset
        serializer = NewAddSerializer(queryset, many=True)

        # Return the serialized data as response
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        ad_serializer = NewAddSerializer(data=request.data)
        if ad_serializer.is_valid():
            
            ad_management = ad_serializer.save()
            # Prepare invoice data after ad creation
            admin_user = User.objects.filter(is_superuser=True).first()
            invoice_data = {
                'invoice_type': ad_management.ad_category.ad_type,
                'sender': ad_management.ad_user.id,
                'receiver': admin_user.id,
                'price': ad_management.total_amount,
                'total_amount': ad_management.total_amount,
                'invoice_date': ad_management.valid_from,
                'appointment_date': ad_management.valid_from
            }
            # Create invoice
            invoice_serializer = InvoiceSerializer(data=invoice_data)
            if invoice_serializer.is_valid():
                invoice_serializer.save()
            else:
                return Response(invoice_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Return response for the ad and invoice creation
            return Response({
                "ad_management": ad_serializer.data,
                "invoice": invoice_serializer.data
            }, status=status.HTTP_201_CREATED)
        # Handle errors in ad creation
        return Response(ad_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
           
    # PUT: Update an existing advertisement

    def put(self, request, pk, *args, **kwargs):
        # Retrieve the ad using the primary key from the URL
        ad = get_object_or_404(Ad_Management, id=pk)

        # Create a serializer with partial updates allowed
        serializer = NewAddSerializer(ad, data=request.data, partial=True)
        
        if serializer.is_valid():
            ad = serializer.save()
            return Response(NewAddSerializer(ad).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request, *args, **kwargs):
            id = request.data.get('id')
            try:
                ad = Ad_Management.objects.get(id=id)
                ad.delete()
                return Response({'message': 'Ad deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
            except Ad_Management.DoesNotExist:
                return Response({'error': 'Ad not found.'}, status=status.HTTP_404_NOT_FOUND)

class PayoutScheduleView(APIView):

    def post(self, request, *args, **kwargs):
        """Conditional data retrieval based on inputs."""
        user_type = request.data.get('user_type')
        user_id = request.data.get('user_id')
        auto_payment_schedule = request.data.get('auto_payment_schedule')
        manual_payout_schedule = request.data.get('manual_payout_schedule')
        #payoutserializer=PayoutScheduleSerializer(data=request.data)

        # Check if user_type is provided
        if not user_type:
            return Response({"error": "user type is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user_id:
            if auto_payment_schedule:
                # Check for duplicates
                existing_schedule = PayoutSchedule.objects.filter(user_type=user_type,auto_payment_schedule=auto_payment_schedule).first()
                if existing_schedule:
                    return Response({"error": "Duplicate entry for auto_payment_schedule."},status=status.HTTP_400_BAD_REQUEST)

                data = {
                    "user_type": user_type,
                    "auto_payment_schedule": auto_payment_schedule,}

                payoutserializer = PayoutScheduleSerializer(data = data)
                if payoutserializer.is_valid():
                    payoutserializer.save()
                    return Response(payoutserializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(payoutserializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Handle case when user_id is provided
        if user_id:
            # Fetch associated account details
            account_details = AccountDetails.objects.filter(user_id=user_id).first()
            existing_payout_schedule = PayoutSchedule.objects.filter(user_id=user_id).first()
            
            if not account_details:
                return Response({"error": "Account details not found for the provided user_id."}, status=status.HTTP_404_NOT_FOUND)
            elif existing_payout_schedule:
                return Response({"error": "Payout Schedule existing for the same user."},status=status.HTTP_400_BAD_REQUEST)
            data = {
                    "user_type": user_type,
                    "user_id" : user_id,
                    "manual_payment_schedule" : request.data.get("manual_payment_schedule"),
                    "manual_payment_amount" : request.data.get("manual_payment_amount"),
                    "auto_payment_schedule": None}

            payoutserializer = PayoutScheduleSerializer(data=data)
            account_serializer = AccountDetailsSerializer(account_details)

            # Validate and save the payout schedule
            if payoutserializer.is_valid():
                payoutserializer.save()
                return Response(payoutserializer.data, status=status.HTTP_201_CREATED)
            else:
                print("Validation errors:", payoutserializer.errors)
                return Response(payoutserializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if not account_details.account_number:
                response_data = {
                    'Scheduled_date': payoutserializer.data,
                    'Account details': account_serializer.data,
                    'Bank Account': 'Update Account Details'
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                data = {
                    'Scheduled_date': payoutserializer.data,
                    'Account details': account_serializer.data
                }
                return Response(data, status=status.HTTP_200_OK)
            
            return Response(payoutserializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Fetch the account details for the given user_id
            account = AccountDetails.objects.get(user_id=user_id)
            user_schedule = PayoutSchedule.objects.get(user_id=user_id)
        except AccountDetails.DoesNotExist:
            return Response({"error": "Account not found."}, status=status.HTTP_404_NOT_FOUND)

        # Partially update the account details with the provided data
        accountserializer = AccountDetailsSerializer(account, data=request.data, partial=True)
        payoutserializer = None

        # If user_schedule exists, perform a partial update
        if user_schedule:
            payoutserializer = PayoutScheduleSerializer(user_schedule, data=request.data, partial=True)
        
        if accountserializer.is_valid():
            accountserializer.save()
        
        if payoutserializer and payoutserializer.is_valid():
            payoutserializer.save()

        # Prepare the response data
        response_data = {
            "account_details": accountserializer.data
        }
        
        if payoutserializer:
            response_data["payout_schedule"] = payoutserializer.data

        return Response(response_data, status=status.HTTP_200_OK) if accountserializer.is_valid() else Response(accountserializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        user_type = request.data.get('user_type')
        # If user_id is not provided, return all payout schedules
        if user_type:
            if not user_id:
                user_schedule = PayoutSchedule.objects.filter(user_type = user_type).first()
                user_schedule_serializer = PayoutScheduleSerializer(user_schedule)
                return Response(user_schedule_serializer.data, status=status.HTTP_200_OK)

        if not user_id:
            schedules = PayoutSchedule.objects.all()
            payoutserializer = PayoutScheduleSerializer(schedules, many=True)
            return Response(payoutserializer.data, status=status.HTTP_200_OK)

        # If a specific user_id is provided
        else:
            # Filter schedules and account info based on user_id
            user_schedule = PayoutSchedule.objects.filter(user_id=user_id)
            account_info = AccountDetails.objects.filter(user_id=user_id)

            # Serialize the filtered objects
            user_schedule_serializer = PayoutScheduleSerializer(user_schedule, many=True)
            account_info_serializer = AccountDetailsSerializer(account_info, many=True)

            # Return serialized data for the specific user
            return Response({
                'payment_scheduled': user_schedule_serializer.data,
                'account_details': account_info_serializer.data
            }, status=status.HTTP_200_OK)


        
        
