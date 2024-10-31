from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomerSerializer, UnifiedResponseSerializer
from Accounts.models import Customer, Subcategory,ServiceRegister,ServiceRequest,Payment,User,Invoice
from .serializers import Customerview_Serializer, SubcategorySerializer,ExpensesSerializer,AdsInvoiceSerializer,ExpenseTableSerializer,EarningsSerializer
from rest_framework.decorators import action
from .pagination import CustomerViewPagination
# from .pagination import AdsInvoicePagination,ExpensePagination
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum,Q
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination



# Create your views here.




# ********************  ADD NEW USER *********************

class UserCreateView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def perform_create(self, serializer):
        # Auttomatically set is_customer = True in the serializer 
        serializer.save()





# ************************  USERS-USER MANAGEMENT  ************************* 

class CustomerListView(generics.ListAPIView):
    queryset = Customer.objects.all()             # Fetch all customers
    serializer_class = Customerview_Serializer
    pagination_class = CustomerViewPagination    # Apply custom pagination




# ********************* SUBCATEGORY - ADD NEW  **************************

class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)

        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status = status.HTTP_201_CREATED, headers = headers)
    
    def perform_create(self, serializer):
        serializer.save()


# Custom action for deletion (DELETE)
    @action(detail=False, methods=['delete'], url_path = 'delete')
    def delete_subcategory(self, request):
        subcategory_id = request.data.get('id')
        if not subcategory_id:
            return Response({"error":"subcategory_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        subcategory = get_object_or_404(Subcategory, id = subcategory_id)

        # First, delete all ServiceRequest instances related to this Subcategory  ----  Django's double underscore (__) notation to traverse relationships between models. 
        ServiceRequest.objects.filter(service__subcategory = subcategory).delete()          # service: This refers to a foreign key field in the ServiceRequest model that links to the ServiceRegister mode

        # Then, delete all ServiceRegister instances related to this Subcategory
        ServiceRegister.objects.filter(subcategory = subcategory).delete()        # subcategory is a foreign key on ServiceRegister

        # Now delete the Subcategory
        self.perform_destroy(subcategory)       # to delete the subcategory itself
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
        instance.delete()


# custom action to get subcategories by category id
    @action(detail = False, methods = ['post'], url_path = 'by-category')
    def get_subcategories_by_category(self, request):
        category_id = request.data.get('id')

        if not category_id:
            return Response({"error": "category_id is required"}, status = status.HTTP_400_BAD_REQUEST)
        subcategories = Subcategory.objects.filter(category_id = category_id)
        serializer = self.get_serializer(subcategories, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)


 # Custom action for updating a subcategory (PUT/PATCH)
    @action(detail=False, methods = ['put', 'patch'], url_path='update')
    def update_subcategory(self, request):
        subcategory_id = request.data.get('id')

        if not subcategory_id:
            return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
        subcategory = get_object_or_404(Subcategory, id = subcategory_id)

        serializer = self.get_serializer(subcategory, data = request.data, partial=request.method == 'PATCH')
        serializer.is_valid(raise_exception = True)
        self.perform_update(serializer)
        return Response(serializer.data)
    def perform_update(self, serializer):
        serializer.save()







# *****************************  Financial Management  ***********************************



User = get_user_model()

class AdsInvoicePagination(PageNumberPagination):
    page_size = 2  # Customize page size for ads invoices
    page_size_query_param = 'page_size'
    max_page_size = 100

class ExpensePagination(PageNumberPagination):
    page_size = 2  # Customize page size for expense table
    page_size_query_param = 'page_size'
    max_page_size = 100

class UnifiedView(APIView):
    def get(self, request):
        data_type = request.query_params.get('data_type')

        if data_type == 'ads':
            return self.handle_ads_invoices(request)
        elif data_type == 'expense':
            return self.handle_expense_table(request)
        else:
            return self.handle_all_data(request)

    def handle_ads_invoices(self, request):
        ads_invoices = self.get_ads_invoices()
        ads_paginator = AdsInvoicePagination()
        paginated_ads_invoices = ads_paginator.paginate_queryset(ads_invoices, request)
        return ads_paginator.get_paginated_response(paginated_ads_invoices)

    def handle_expense_table(self, request):
        admin_user = self.get_admin_user()
        expense_table = self.get_expense_table(admin_user)
        expense_paginator = ExpensePagination()
        paginated_expense_table = expense_paginator.paginate_queryset(expense_table, request)
        return expense_paginator.get_paginated_response(paginated_expense_table)

    def handle_all_data(self, request):
        admin_user = self.get_admin_user()

        # Get and paginate ads invoices
        ads_invoices = self.get_ads_invoices()
        ads_paginator = AdsInvoicePagination()
        paginated_ads_invoices = ads_paginator.paginate_queryset(ads_invoices, request)

        # Get and paginate expense table
        expense_table = self.get_expense_table(admin_user)
        expense_paginator = ExpensePagination()
        paginated_expense_table = expense_paginator.paginate_queryset(expense_table, request)

        # Prepare the response data
        response_data = {
            "total_expenses": self.calculate_expenses(admin_user),
            "total_earnings": self.calculate_earnings(admin_user),
            "ads_invoices": paginated_ads_invoices,
            "expense_table": paginated_expense_table,
        }
        return Response(response_data)

    def get_admin_user(self):
        try:
            return User.objects.get(is_superuser=True)
        except User.DoesNotExist:
            return Response({"error": "No superuser found"}, status=404)

    def calculate_expenses(self, admin_user):
        return Payment.objects.filter(sender=admin_user, payment_status='completed').aggregate(total=Sum('amount_paid'))['total'] or 0

    def calculate_earnings(self, admin_user):
        return Payment.objects.filter(receiver=admin_user, payment_status='completed').aggregate(total=Sum('amount_paid'))['total'] or 0

    def get_ads_invoices(self):
        ads_invoices = Invoice.objects.filter(invoice_type='Ads').prefetch_related('payments').select_related('sender')
        results = []
        for invoice in ads_invoices:
            user_type = self.get_user_type(invoice.sender)
            first_payment = invoice.payments.first()
            results.append({
                'transaction_id': first_payment.transaction_id if first_payment else None,
                'sender': invoice.sender.full_name,
                'amount': first_payment.amount_paid if first_payment else None,
                'sender_user_type': user_type,
                'payment_date': first_payment.payment_date if first_payment else None,
            })
        return results

    def get_expense_table(self, admin_user):
        payments = Payment.objects.filter(sender=admin_user).select_related('invoice')
        results = [
            {
                'invoice_type': payment.invoice.invoice_type,
                'transaction_id': payment.transaction_id,
                'amount_paid': payment.amount_paid,
                'transaction_date': payment.payment_date
            }
            for payment in payments
        ]
        return results

    def get_user_type(self, sender):
        if sender.is_superuser:
            return 'Admin'
        elif sender.is_customer:
            return 'Customer'
        elif sender.is_service_provider:
            return 'Service Provider'
        elif sender.is_franchisee:
            return 'Franchisee'
        elif sender.is_dealer:
            return 'Dealer'
        else:
            return 'Unknown'
