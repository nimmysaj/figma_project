from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from Accounts.models import Franchise_Type, ServiceRequest, ServiceProvider#, Franchisee
from rest_framework import serializers
from .serializer import Franchise_Type_Serializer, ServiceHistorySerializer#, FranchiseeDetailsSerializer
from rest_framework import status
from rest_framework.pagination import PageNumberPagination  # Import pagination class
from django.core.paginator import Paginator

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

# class FranchiseeDetailsView(APIView):
#     # To view franchisee details based on entered franchisee custom ID
    
#     def post(self, request, *args, **kwargs):
#         # Extract franchisee_cust_id from the request body
#         franchisee_cust_id = request.data.get('franchisee_cust_id')

#         if not franchisee_cust_id:
#             return Response(
#                 {"error": "Franchisee ID is required."},status=status.HTTP_400_BAD_REQUEST
#             )

#         # Query the franchisee based on the given custom_id
#         franchisee = Franchisee.objects.filter(custom_id=franchisee_cust_id).first()

#         if not franchisee:
#             return Response(
#                 {"error": "Franchisee not found."},status=status.HTTP_404_NOT_FOUND
#             )

#         # Serialize the franchisee object
#         serialized_frdata = FranchiseeDetailsSerializer(franchisee).data

#         return Response(serialized_frdata, status=status.HTTP_200_OK)