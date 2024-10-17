from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import generics
from Accounts.models import Franchise_Type,ServiceRequest,Franchisee
from .serializers import FranchiseTypeSerializer,ServiceHistorySerializer,FranchiseeDetailsSerializer
from django.shortcuts import get_object_or_404


class AddFranchiseType(APIView):
    

    def get(self, request):
        
        queryset = Franchise_Type.objects.all()
        serializer= FranchiseTypeSerializer(queryset ,many=True)
        return Response(serializer.data)

    def post(self, request):
        # Create a new Franchisee Type object
        serializer = FranchiseTypeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # Update an existing Person object
        try:
            frtype= Franchise_Type.objects.get(id=request.data['id'])
        except Franchise_Type.DoesNotExist:
            return Response({"error": "Franchisee not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FranchiseTypeSerializer(frtype, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        # Partially update an existing  franchise type
        try:
            frtype = Franchise_Type.objects.get(id=request.data['id'])
        except Franchise_Type.DoesNotExist:
            return Response({"error": "Franchisee not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FranchiseTypeSerializer(frtype, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Delete a franchisee type
        try:
            frtype = Franchise_Type.objects.get(id=request.data['id'])
        except Franchise_Type.DoesNotExist:
            return Response({"error": "Franchisee not found"}, status=status.HTTP_404_NOT_FOUND)

        frtype.delete()
        return Response({"message": "Franchisee Type deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size=10
    page_size_query_param='page'
     
class ServiceHistoryView_get(APIView):
    """
    View to get service history for service requests with 'accepted' or 'pending' statuses.
    """
    def get(self, request):
        paginator_class=CustomPagination
        # Extract the franchisee_id from the POST request data
        
        paginator=self.paination_class()
        
        # Filter service requests with 'accepted' or 'pending' statuses for the given franchisee
        service_requests = ServiceRequest.objects.filter(work_status__in=['in_progress', 'pending', 'completed'])
       
        total_jobs=ServiceRequest.objects.count()
        total_active_jobs=ServiceRequest.objects.filter(work_status='in_progress').count()
        total_completed_jobs=ServiceRequest.objects.filter(work_status='completed').count()
        paginated_requests =paginator.paginate_queryset(service_requests, request,view=self)
        # Serialize the filtered service requests
        serializer = ServiceHistorySerializer(paginated_requests, many=True).data

        # Return the serialized data as the response
        return Response({"Total_jobs":total_jobs,
                        "Active_jobs":total_active_jobs,
                        "Completed_jobs":total_completed_jobs,
                        "Service History":serializer}, status=status.HTTP_200_OK)
          

class ServiceHistoryView(APIView):
    paginator=CustomPagination()
    """
    View to get service history for service requests with 'accepted' or 'pending' statuses.
    """
    def post(self, request):
        
        # Extract the franchisee_id from the POST request data
        franchisee_id = request.data.get('franchisee_id')

        if not franchisee_id:
            return Response({"error": "Franchisee ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the franchisee object
        franchisee = get_object_or_404(Franchisee, custom_id=franchisee_id)
        #paginator=paginator_class.paination_class()
        
        # Filter service requests with 'accepted' or 'pending' statuses for the given franchisee
        service_requests = ServiceRequest.objects.filter(
            service_provider__franchisee=franchisee,
            work_status__in=['in_progress', 'pending', 'completed'])
       
        total_jobs=service_requests.count()
        total_active_jobs=service_requests.filter(work_status='in_progress').count()
        total_completed_jobs=service_requests.filter(work_status='completed').count()
        paginated_requests =self.paginator.paginate_queryset(service_requests,request,view=self)
        # Serialize the filtered service requests
        serializer = ServiceHistorySerializer(paginated_requests, many=True).data
        #paginated_response=self.paginator.get_paginated_response(serializer)

        # Return the serialized data as the response
        return self.paginator.get_paginated_response({"Total_jobs":total_jobs,
                        "Active_jobs":total_active_jobs,
                        "Completed_jobs":total_completed_jobs,
                        "Service History":serializer})
        
class FranchiseeDetailsView(APIView):
    def get(self, request):
        
        queryset = Franchisee.objects.all()
        serializer= FranchiseeDetailsSerializer(queryset ,many=True)
        return Response(serializer.data)

    
    