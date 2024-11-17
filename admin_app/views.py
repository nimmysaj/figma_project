from django.shortcuts import render
from rest_framework import permissions ,generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from Accounts.models import User ,Payment ,Franchisee ,Service_Type ,Collar ,Ad_category ,Invoice ,Payment 
from .serializers import *
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.decorators import action
from django.db import transaction
from django.conf import settings
import razorpay


class FranchiseeView(APIView):
    permission_classes = [IsAuthenticated]  # Only accessible by admins

    def post(self, request):
        """Register a new franchisee along with a new user"""
        try:
            with transaction.atomic():
                serializer = FranchiseeSerializer(data=request.data)
                if serializer.is_valid():
                    franchisee = serializer.save()
                    invoice = self.create_invoice(franchisee)
                    
                    invoice_serializer = InvoiceSerializer(invoice)
                    return Response({
                        'franchisee': serializer.data,
                        'invoice': invoice_serializer.data
                    }, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def create_invoice(self, franchisee):
        """Create an invoice for franchisee registration"""
        # Assume that the admin user is the first user (or you can adjust this logic)
        admin_user = User.objects.filter(is_superuser=True).first()
        
        # amount to pay
        amount = franchisee.type.amount
        if amount is None or amount <= 0:
            raise ValidationError("Invalid amount specified for franchisee registration.")

        if not admin_user:
            return Response({"error": "Admin user not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the invoice for franchisee registration
        invoice = Invoice.objects.create(
            # invoice_number=self.generate_invoice_number(),
            invoice_type='franchisee_registration',
            sender=franchisee.user,  # Franchisee is the sender
            receiver=admin_user,     # Admin is the receiver
            description="Franchisee Registration Fee",
            price=amount,  # Set an appropriate price
            total_amount=amount,
            payment_status='pending',  # Initially, the payment status is pending
            accepted_terms=True
            # invoice_date=timezone.now(),
            # due_date=timezone.now() + timezone.timedelta(days=30),  # Set due date
        )
        return invoice

    
    def get(self, request):
        """Retrieve franchisee details based on ID in the body"""
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "USER ID is required in the body"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            franchisee = Franchisee.objects.get(user=user_id)
            serializer = FranchiseeSerializer(franchisee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Franchisee.DoesNotExist:
            return Response({"error": "Franchisee not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        """Update an entire franchisee record based on ID in the body"""
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "USER ID is required in the body"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            franchisee = Franchisee.objects.get(user=user_id)
            serializer = FranchiseeSerializer(franchisee, data=request.data)

            # Check if the serializer is valid
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Franchisee.DoesNotExist:
            return Response({"error": "Franchisee not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        """Partially update a franchisee record based on ID in the body"""
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "user ID is required in the body"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            franchisee = Franchisee.objects.get(user=user_id)
            serializer = FranchiseeSerializer(franchisee, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Franchisee.DoesNotExist:
            return Response({"error": "Franchisee not found"}, status=status.HTTP_404_NOT_FOUND)


class TransactionPagination(PageNumberPagination):
    page_size = 10  # Number of items per page
    page_size_query_param = 'page_size'  # Allows clients to set the page size
    max_page_size = 100  # Maximum limit for page size

class TransactionListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = TransactionSerializer
    pagination_class = TransactionPagination


# TASK 3 SERVICE TYPE CRUD //////////////////////////////////////////////////////////////////////////////////////////////////

class ServiceTypeAPIView(APIView):
    
    def post(self, request):
        """Create a new service type with validation."""
        serializer = ServiceTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Retrieve a specific service type by ID or get all if no ID is provided."""
        service_id = request.data.get('id')
        
        if service_id:
            try:
                service = Service_Type.objects.get(id=service_id)
                serializer = ServiceTypeSerializer(service)
                return Response(serializer.data)
            except Service_Type.DoesNotExist:
                return Response({"error": "Service type not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # If no ID is provided, return all service types.
            services = Service_Type.objects.all()
            serializer = ServiceTypeSerializer(services, many=True)
            return Response(serializer.data)

    def put(self, request):
        """Update a service type (replace all fields)."""
        service_id = request.data.get('id')
        if not service_id:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service_Type.objects.get(id=service_id)
            serializer = ServiceTypeSerializer(service, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Service_Type.DoesNotExist:
            return Response({"error": "Service type not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        """Partially update a service type."""
        service_id = request.data.get('id')
        if not service_id:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service_Type.objects.get(id=service_id)
            serializer = ServiceTypeSerializer(service, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Service_Type.DoesNotExist:
            return Response({"error": "Service type not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        """Delete a service type."""
        service_id = request.data.get('id')
        if not service_id:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service_Type.objects.get(id=service_id)
            service.delete()
            return Response({"message": "Service type deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Service_Type.DoesNotExist:
            return Response({"error": "Service type not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
# TASK 3 Collor CRUD //////////////////////////////////////////////////////////////////////////////////////////////////


class CollarAPIView(APIView):

    def post(self, request):
        """Create a new collar."""
        serializer = CollarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Retrieve a specific collar by ID or all collars if no ID is provided."""
        collar_id = request.data.get('id')
        if collar_id:
            try:
                collar = Collar.objects.get(id=collar_id)
                serializer = CollarSerializer(collar)
                return Response(serializer.data)
            except Collar.DoesNotExist:
                return Response({"error": "Collar not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            collars = Collar.objects.all()
            serializer = CollarSerializer(collars, many=True)
            return Response(serializer.data)

    def put(self, request):
        """Fully update a collar."""
        collar_id = request.data.get('id')
        if not collar_id:
            return Response({"error": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            collar = Collar.objects.get(id=collar_id)
            serializer = CollarSerializer(collar, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Collar.DoesNotExist:
            return Response({"error": "Collar not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        """Partially update a collar."""
        collar_id = request.data.get('id')
        if not collar_id:
            return Response({"error": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            collar = Collar.objects.get(id=collar_id)
            serializer = CollarSerializer(collar, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Collar.DoesNotExist:
            return Response({"error": "Collar not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        """Delete a collar."""
        collar_id = request.data.get('id')
        if not collar_id:
            return Response({"error": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            collar = Collar.objects.get(id=collar_id)
            collar.delete()
            return Response({"message": "Collar deleted."}, status=status.HTTP_204_NO_CONTENT)
        except Collar.DoesNotExist:
            return Response({"error": "Collar not found."}, status=status.HTTP_404_NOT_FOUND)

# TASK 3 GET Service Type and Collor Details

class ServiceTypeAndCollarView(APIView):
    """View to retrieve both ServiceType and Collar data."""

    def get(self, request, *args, **kwargs):
        # Fetch all ServiceType and Collar objects
        service_types = Service_Type.objects.all()
        collars = Collar.objects.all()

        # Serialize the data
        service_type_serializer = ServiceTypeSerializer(service_types, many=True)
        collar_serializer = CollarSerializer(collars, many=True)

        # Return both in a single response
        return Response(
            {
                'service_types': service_type_serializer.data,
                'collars': collar_serializer.data
            },
            status=status.HTTP_200_OK
        )








# TASK 4 Ad Category CRUD Operations //////////////////////////////////////////////////////////////////////////////////////////////////

        
class AdCategoryAPIView(APIView):

    def get_ad_category(self, pk):
        """Helper method to retrieve Ad Category by ID."""
        try:
            return Ad_category.objects.get(pk=pk)
        except Ad_category.DoesNotExist:
            return None

    def get(self, request):
        """Retrieve an Ad Category by ID or all Ad Categories."""
        pk = request.data.get('id', None)
        if pk:
            ad_category = self.get_ad_category(pk)
            if ad_category:
                serializer = AdCategorySerializer(ad_category)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"error": "Ad Category not found"}, status=status.HTTP_404_NOT_FOUND)
        
        ad_categories = Ad_category.objects.all()
        serializer = AdCategorySerializer(ad_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new Ad Category."""
        serializer = AdCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Update an Ad Category completely using ID from the request body."""
        pk = request.data.get('id', None)  # Extract ID from the request body
        ad_category = self.get_ad_category(pk)  # Retrieve the current Ad Category

        if ad_category:
            # Pass the existing instance to the serializer
            serializer = AdCategorySerializer(ad_category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Ad Category not found or ID not provided"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        """Partially update an Ad Category using ID from the request body."""
        pk = request.data.get('id', None)
        ad_category = self.get_ad_category(pk)

        if ad_category:
            serializer = AdCategorySerializer(ad_category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"error": "Ad Category not found or ID not provided"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        """Delete an Ad Category using ID from the request body."""
        pk = request.data.get('id', None)
        ad_category = self.get_ad_category(pk)

        if ad_category:
            ad_category.delete()
            return Response({"message": "Ad Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        
        return Response({"error": "Ad Category not found or ID not provided"}, status=status.HTTP_404_NOT_FOUND)
    

# Add Expense

class AddExpenseView(APIView):

    def post(self, request):
        serializer = AddExpensesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get_invoice(self, pk):
        
        try:
            return Invoice.objects.get(pk=pk,invoice_type='others')
        except Invoice.DoesNotExist:
            return None

    def get(self, request):
        
        pk = request.data.get('id', None)
        if pk:
            Expense = self.get_invoice(pk)
            if Expense:
                serializer = AddExpensesSerializer(Expense)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)
        
        Expenses = Invoice.objects.filter(invoice_type='others')
        serializer = AddExpensesSerializer(Expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        pk = request.data.get('id', None)
        if pk is None:
            return Response({"error": "ID is required for updating an invoice"}, status=status.HTTP_400_BAD_REQUEST)

        expense = self.get_invoice(pk)
        if expense is None:
            return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AddExpensesSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        pk = request.data.get('id', None)
        if pk is None:
            return Response({"error": "ID is required for updating an invoice"}, status=status.HTTP_400_BAD_REQUEST)

        expense = self.get_invoice(pk)
        if expense is None:
            return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AddExpensesSerializer(expense, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pk = request.data.get('id', None)
        if pk is None:
            return Response({"error": "ID is required for deleting an invoice"}, status=status.HTTP_400_BAD_REQUEST)

        expense = self.get_invoice(pk)
        if expense is None:
            return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

        expense.delete()
        return Response({"message": "Invoice deleted successfully"}, status=status.HTTP_204_NO_CONTENT)