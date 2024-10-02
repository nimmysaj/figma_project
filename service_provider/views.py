from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from copy import deepcopy
from Accounts.models import ServiceRequest, ServiceProvider
from .serializers import (
    ServiceRequestSerializer, 
    CustomerServiceRequestSerializer,
    InvoiceSerializer
    )

from rest_framework import status
from Accounts.models import User
from django.contrib.auth import get_user_model

User = get_user_model() 
        

class ServiceProviderRequestsView(APIView):
    # permission_classes = [IsAuthenticated]

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
    # permission_classes = [IsAuthenticated]

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
    # permission_classes = [IsAuthenticated]

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
        response_data = serializer.data
        response_data['work_status'] = service_request.work_status
        return Response(response_data, status=200)

    def post(self, request, pk, *args, **kwargs):
        # Fetch the service request for which the invoice is being created
        service_request = get_object_or_404(ServiceRequest, pk=pk)

        # Check if the logged-in user is the service provider for the request
        if service_request.service_provider != request.user:
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
                "error": "Cannot generate invoice. Work is pending."
            }, status=status.HTTP_400_BAD_REQUEST)
    
        elif service_request.acceptance_status == 'decline':
            return Response({
                "error": "Cannot generate invoice. Work has been declined."
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
                
                if service_request.work_status != 'in_progress':
                    service_request.work_status = 'in_progress'
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