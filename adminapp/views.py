from datetime import timezone
from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomerSerializer, UnifiedResponseSerializer
from Accounts.models import Customer, Subcategory,ServiceRegister,ServiceRequest,Payment,User,Invoice
from .serializers import Customerview_Serializer, SubcategorySerializer,ExpensesSerializer,AdsInvoiceSerializer,ExpenseTableSerializer,EarningsSerializer,MonthlyFinanceReportSerializer
from rest_framework.decorators import action,api_view
from .pagination import CustomerViewPagination
# from .pagination import AdsInvoicePagination,ExpensePagination
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum,Q
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
import razorpay
from datetime import datetime


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
        





# # ***************************************  PAYMENT INTEGRATION USING RAZORPAY  ***************************************



# # function to list invoice ids:
# @api_view(['GET'])
# def get_invoice_ids(request):
#     invoice_ids = Invoice.objects.values_list('id', flat=True)  # Get a list of invoice IDs
#     return Response({'invoice_ids': list(invoice_ids)})


# class CreateRazorpayOrder(APIView):
#     def post(self, request, *args, **kwargs):
#         # Initialize Razorpay client
#         client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID , settings.RAZORPAY_SECRET_KEY))
        
#         # Get the invoice and calculate the amount to be paid
#         invoice_id = request.data.get("invoice_id")
#         invoice = Invoice.objects.get(id=invoice_id)
#         amount = int(invoice.total_amount * 100)  # Amount in paisa-- int()use to get a precise integer representation

#         # Create an order in Razorpay
#         razorpay_order = client.order.create({
#             "amount": amount,
#             "currency": "INR",
#             "payment_capture": 1  # Auto-capture-, you are instructing Razorpay to automatically capture the payment immediately after the order is authorized-
#                                   # If you set "payment_capture": 0, the payment will be authorized but not captured. In this case, you would need to explicitly call the capture API to complete the payment later.
#         })

#         # Save Razorpay order ID to the Payment model
#         payment = Payment.objects.create(
#             invoice=invoice,
#             sender=invoice.sender,
#             receiver=invoice.receiver,
#             order_id=razorpay_order['id'],
#             amount_paid=invoice.total_amount,
#             payment_status='pending'
#         )

#         return Response({
#             "order_id": razorpay_order['id'],
#             "amount": amount,
#             "currency": "INR",
#             "razorpay_key": settings.RAZORPAY_KEY_ID
#         })

# @api_view(['POST'])   # its a decorator that transforms a regular Python function into a view that can handle HTTP requests
# def handle_payment_success(request):
#     payment_id = request.data.get('razorpay_payment_id')
#     order_id = request.data.get('razorpay_order_id')
#     signature_id = request.data.get('razorpay_signature')

#     client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
#     # Verify the payment signature
#     try:
#         client.utility.verify_payment_signature({
#             'razorpay_order_id': order_id,
#             'razorpay_payment_id': payment_id,
#             'razorpay_signature': signature_id
#         })
#     except razorpay.errors.SignatureVerificationError:
#         return Response({'error': 'Signature verification failed'}, status=400)
    
#     # If verified, update the Payment and Invoice status
#     try:
#         payment = Payment.objects.get(order_id=order_id)
#     except Payment.DoesNotExist:
#         return Response({"error": "Payment not found"}, status=404)

#     payment.transaction_id = payment_id
#     payment.payment_status = 'completed'
#     payment.payment_date = timezone.now()
#     payment.save()

#     # Mark the invoice as paid
#     payment.invoice.mark_paid()

#     return Response({
#         'order_id': order_id,
#         'transaction_id': payment_id,
#         'signature_id': signature_id,
#         'status': 'Payment successful'
#     })






# ************************************  GRAPH - PHINANCIAL MANAGEMENT  *******************************************

# class MonthlyFinanaceReportView(generics.GenericAPIView):
#     serializer_class = MonthlyFinanceReportSerializer
#     # permission_classes = IsAuthenticated

#     def post(self, request):
#         # Validate the incoming data using the serializer
#         serializer = self.get_serializer(data = request.data)
#         serializer.is_valid(raise_exception = True)

#         month = serializer.validated_data['month']
#         year = serializer.validated_data['year']

#         # Get the start and end dates for the specified month
#         start_date = datetime(year, month, 1)
#         if month == 12:
#             end_date = datetime(year+1, 1, 1)  #January of the next year
#         else:
#             end_date = datetime(year, month+1, 1) #First day of the next month

#         # Calculate total expenses where sender is admin and payment status is completed
#         total_expense = Payment.objects.filter(
#             sender__is_staff = True, #Check if the sender is admin
#             payment_status = 'completed',
#             payment_date__gte = start_date,   #gte- greater than or equal to
#             payment_date__lt = end_date       #lt - less than
#         ).aggregate(total=Sum('amount_paid'))['total'] or 0    #['total'] is a dictionary it holds the sum of amount_paid field-- eg: 'total':1500

#         # Calculate total income where receiver is admin and payment status is completed
#         total_income = Payment.objects.filter(
#             receiver__is_staff = True,    #In Django's built-in User model, the field for admin users is typically is_staff (not is_admin), so use sender__is_staff
#             payment_status = 'completed',
#             payment_date__gte = start_date,
#             payment_date__lt = end_date
#         ).aggregate(total=Sum('amount_paid'))['total'] or 0

#         # Return the results
#         return Response(
#             {
#                 'total_expense' : total_expense,
#                 'total_income' : total_income
#             }
#         )

class MonthlyFinanaceReportView(generics.GenericAPIView):
    serializer_class = MonthlyFinanceReportSerializer
    # permission_classes = IsAuthenticated

    def post(self, request):
        # Validate the incoming data using the serializer (only year is needed now)
        serializer = self.get_serializer(data = request.data)    #create instance of serializer
        serializer.is_valid(raise_exception = True)



        year = serializer.validated_data['year']     #Get the year from the requested data

        # Calculate the total expenses and income for each month of the specified year
        monthly_data = []
        for month in range(1, 13):
            # Get the start and end dates for the specified month
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year+1, 1, 1)  #January of the next year
            else:
                end_date = datetime(year, month+1, 1) #First day of the next month

            # Calculate total expenses where sender is admin and payment status is completed
            total_expense = Payment.objects.filter(
                sender__is_staff = True, #Check if the sender is admin
                payment_status = 'completed',
                payment_date__gte = start_date,   #gte- greater than or equal to
                payment_date__lt = end_date       #lt - less than
            ).aggregate(total=Sum('amount_paid'))['total'] or 0    #['total'] is a dictionary it holds the sum of amount_paid field-- eg: 'total':1500

            # Calculate total income where receiver is admin and payment status is completed
            total_income = Payment.objects.filter(
                receiver__is_staff = True,    #In Django's built-in User model, the field for admin users is typically is_staff (not is_admin), so use sender__is_staff
                payment_status = 'completed',
                payment_date__gte = start_date,
                payment_date__lt = end_date
            ).aggregate(total=Sum('amount_paid'))['total'] or 0

            # Append the data for the month
            monthly_data.append(
                {
                    'month' : month,
                    'total_expense' : total_expense,
                    'total_income ' : total_income
                }
            )

            # Return the monthly totals for the entire year
        return Response({
                        'year':year, 
                        'monthly_data' : monthly_data
                        })

