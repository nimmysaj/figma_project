from datetime import datetime
import random
import re
from rest_framework import serializers
from Accounts.models import Customer, User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from Accounts.models import ServiceRequest, Customer, Subcategory, Invoice, Payment, IncomeManagement
from django.utils import timezone




# ******************************  ADD NEW USER  ******************************************************

class UserSerializer(serializers.ModelSerializer):   # serializers.ModelSerializer - parent cls of UserSerializer 
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User 
        fields = ['full_name','address','landmark','pin_code','district','state','watsapp','email','phone_number',
                  'country_code','password','joining_date']
    
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")

        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")

        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")

        if not re.search(r'[@$!%*?&]', value):
            raise serializers.ValidationError("Password must contain at least one special character (@, $, !, %, *, ?, &).")
        
        return value
    

    # custom validation for joining date
    def validate_joining_date(self, value):
        # Ensure the joining date is not in the future
        if value > timezone.now().date():
            raise serializers.ValidationError("joining date cannot be in the future.")
        return value
        


    

    def create(self, validated_data):

        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ['user','date_of_birth','gender','profile_image', 'last_activity']


    def create(self, validated_data):
        profile_data = validated_data.pop('user')    #extract user data
        profile_data['password'] = make_password(profile_data['password'])
        user = User.objects.create(**profile_data)   #create user (**profile_data) 
        user.is_customer = True                      #Ensure user is marked as a customer
        user.save()

        customer = Customer.objects.create(user=user, **validated_data)   #create customer data associated with that user
        return customer





# *************************************  USERS - USER MANAGEMENT  ************************************

class Customerview_Serializer(serializers.ModelSerializer):
        # Fields from the User model (related via Customer model)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    joining_date = serializers.DateField(source='user.joining_date', read_only=True)
    address = serializers.CharField(source='user.address', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    


    # Total number of completed services from ServiceRequest model
    completed_services = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'custom_id',           # From Customer model
            'full_name',           # From the User model
            'joining_date',        # From the User model
            'address',             # From the User model
            'phone_number',        # From the User model
            'email',               # From the User model
            'is_active',           # From the User model
            'completed_services'   # Calculated field from Service Request model    
        ]


    # func to calculate total number of completed services

    def get_completed_services(self,obj):
        # Count the number of completed services for this customer
        return ServiceRequest.objects.filter(customer=obj.user, work_status='completed').count()





# ********************************  SUB CATEGORY - ADD NEW   *********************************

class SubcategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Subcategory
        fields = '__all__'




# *******************************  Financial Management  ***********************************

# --> View Total expense
class ExpensesSerializer(serializers.Serializer):
    total_expenses = serializers.DecimalField(max_digits=10, decimal_places=2)


# --> View total earnings
class RevenueSerializer(serializers.Serializer):
    total_revnue = serializers.DecimalField(max_digits=10, decimal_places=2)


# -->view total eranings
class EarningsSerializer(serializers.Serializer):
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)


# --> View user details of Ads invoice
class AdsInvoiceSerializer(serializers.Serializer):
    transaction_id = serializers.CharField()
    sender = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    sender_user_type = serializers.CharField()
    payment_date = serializers.DateTimeField()


# --> View Expense Table
class ExpenseTableSerializer(serializers.Serializer):
    transaction_id = serializers.CharField()
    invoice_type = serializers.CharField()
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = serializers.DateTimeField()


class UnifiedResponseSerializer(serializers.Serializer):
    total_expenses = ExpensesSerializer()
    total_revenue = RevenueSerializer()
    total_earnings = EarningsSerializer()
    ads_invoices = AdsInvoiceSerializer(many=True)
    expense_table = ExpenseTableSerializer(many=True)




  
# # ******************************  PAYMENT INTEGRATION USING RAZORPAY  ******************************

# class InvoiceSerilaizer(serializers.ModelSerializer):
#     class Meta:
#         model = Invoice
#         fields = '__all__'


# class PaymentSerializer(serializers.ModelField):
#     class Meta:
#         model = Payment
#         fields = '__all__'





#**************************************  GRAPH - FINANCIAL MANAGEMENT  **********************************

class MonthlyFinanceReportSerializer(serializers.Serializer):
    year = serializers.IntegerField(min_value = 2000, max_value = 2100)

    def validate_year(self, value):
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError("Year cannot be in the future")
        return value




# ******************************  ACCOUNTS - INVOICE TYPE='OTHERS'  ****************************
# ADD EXPENSE - POST
class InvoiceOthersAddSerializer(serializers.Serializer):
    external_invoice_number = serializers.CharField(required=False, allow_null=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    sender = serializers.IntegerField(required=False, allow_null=True)
    receiver = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField()
    invoice_date = serializers.DateTimeField()
    payment_status = serializers.CharField()
    transaction_type = serializers.ChoiceField(choices=['income', 'expense'])


    def validate_sender(self, value):
        # Sender is only validated if 'expense' transaction_type is passed
        if value is not None and self.initial_data.get('transaction_type')=='expense':    #inital_data--it check th data inside parenthesis b4 any other data get
            try:
                sender_user =  User.objects.get(pk = value)
                return sender_user   #return user instance
            except  User.DoesNotExist:
                raise serializers.ValidationError("Sender User does not exist")
        return value  # If value is None or empty, return as null
    
     # Receiver is only validated if 'income' transaction_type is passed
    def validate_receiver(self, value):
        if value is not None and self.initial_data.get('transaction_type') == 'income':
            try:
                receiver_user = User.objects.get(pk = value)
                return receiver_user
            except User.DoesNotExist:
                return serializers.ValidationError("Receiver user does not exist")
        return value
    

    
#  GET OTHER TYPE ACCOUNTS TABLE
# Serializer for get
class InvoiceOthersGetSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)
    transaction_type = serializers.SerializerMethodField()
    # external_invoice_number = serializers.IntegerField()

    class Meta:
        model = Invoice
        fields = [
            'invoice_number',
            'external_invoice_number',
            'invoice_type',
            'total_amount',
            'sender',
            'receiver',
            'description',
            'invoice_date',
            'invoice_document',
            'transaction_type',
            'sender_username',
            'receiver_username'
        ]

    def get_transaction_type(self, obj):
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            if obj.sender == admin_user:
                return 'Expense'  # Sender is the admin
            elif obj.receiver == admin_user:
                return 'Income'  # Receiver is the admin
        return 'N/A'  # If the sender or receiver is not admin
    
# Serializer for Put, Patch
class InvoiceOthersUpdateSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', required=False)
    receiver_username = serializers.CharField(source='receiver.username', required=False)

    class Meta:
        model = Invoice
        fields = [
            'invoice_number',
            'external_invoice_number',
            'invoice_type',
            'total_amount',
            'sender',
            'receiver',
            'description',
            'invoice_date',
            'invoice_document',
            # 'transaction_type',
            'sender_username',
            'receiver_username'
        ]

    def update(self, instance, validated_data):
        # Handle the case where you want to update sender/receiver by username
        if 'sender_username' in validated_data:
            sender_username = validated_data.pop('sender_username')
            sender = User.objects.get(username=sender_username)
            instance.sender = sender

        if 'receiver_username' in validated_data:
            receiver_username = validated_data.pop('receiver_username')
            receiver = User.objects.get(username=receiver_username)
            instance.receiver = receiver

        # Update remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance




#----------- USER MANAGEMENT -----------
# GET TOTAL NUMBER OF CUSTOMERS
class CustomerCountSerializer(serializers.Serializer):
    total_customers = serializers.IntegerField()


# GET TOTAL NUMBER OF ACTIVE CUSTOMERS
class OnlineCustomerCountSerializer(serializers.Serializer):
    online_customer_count = serializers.IntegerField()

# GET TOTAL SERVICE REQUESTS
class TotalServiceRequestSerializer(serializers.Serializer):
    total_service_requests = serializers.IntegerField()

# GET LEAD REQUESTS COUNT(ONE TIME LEAD)
class LeadRequestCountSerializer(serializers.Serializer):
    lead_request_count = serializers.IntegerField()


# # GET TOTAL ACTIVE SERVICES
class ActiveServiceSerializer(serializers.Serializer):
    active_services = serializers.IntegerField()


# GET TOTAL NUMBER OF COMPLAINTS
class TotalComplaintSerializer(serializers.Serializer):
    total_complaints = serializers.IntegerField()





# # **************************  INCOME MANAGEMENT  ***************************
# class IncomeManagementSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IncomeManagement
#         fields = '__all__'

