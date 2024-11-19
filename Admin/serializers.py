from rest_framework import serializers
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from Accounts.models import Customer,ServiceRequest,CustomerReview,Complaint,Franchisee,ServiceProvider,ServiceRegister,Subcategory,Invoice

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='full_name',read_only=True)
    user_district = serializers.CharField(source='district',read_only=True)
    user_state = serializers.CharField(source='state',read_only=True)
   
    class Meta:
        model = User
        fields=['id','user_name','user_district','user_state']

class UserContactViewSerializer(serializers.ModelSerializer):
    user_whatsappno = serializers.CharField(source='watsapp',read_only=True)
    user_email = serializers.EmailField(source='email',read_only=True)
    user_contactno = serializers.CharField(source='phone_number',read_only=True)

    class Meta:
        model = User
        fields=['id','user_whatsappno','user_email','user_contactno']

class CustomerProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields=['profile_image']

class FranchiseeDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.full_name',read_only=True)
    class Meta:
        model = Franchisee
        fields = ['name']

class ServiceProviderProfileImageSerializer(serializers.ModelSerializer):
    franchisee = FranchiseeDetailSerializer()
    class Meta:
        model=ServiceProvider
        fields=['franchisee','profile_image']

class ComplaintDetailSerializer(serializers.ModelSerializer):
    sender = UserContactViewSerializer()
    class Meta:
        model=Complaint
        fields=['id','subject','description','images','submitted_at','sender']

class ReviewDetailSerializer(serializers.ModelSerializer):
    # customer = UserSerializer()
    # service_provider = UserSerializer()
    class Meta:
        model=CustomerReview
        fields=['id','rating','comment','created_at']

class SubcategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['title']

class ServiceRegisterDetailSerializer(serializers.ModelSerializer):
    subcategory = SubcategoryDetailSerializer()
    class Meta:
        model = ServiceRegister
        fields = ['subcategory']

class InvoiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=Invoice
        fields=['id','appointment_date','invoice_number','quantity','price','total_amount','accepted_terms','additional_requirements']

class ServiceRequestDetailSerializer(serializers.ModelSerializer):
    customer = UserProfileSerializer() # Customer Details
    customer_profile_img = serializers.SerializerMethodField() # Customer Profile Image
    reviews = serializers.SerializerMethodField() # reviews against service request
    complaints_customer = serializers.SerializerMethodField() # Complaints given by the customer to provider against service request
    service_provider = UserProfileSerializer() # Service Provider Details
    provider_detail = serializers.SerializerMethodField() # Provider franchisee name and profile image
    service = ServiceRegisterDetailSerializer() # Service Requested
    invoice = serializers.SerializerMethodField() # Invoice created by service provider to customer based on service request
    complaints_provider = serializers.SerializerMethodField() # Complaints given by provider to customer against service request
    
    class Meta:
        model=ServiceRequest
        fields=['id','customer','customer_profile_img','booking_id','title','work_status','acceptance_status','availability_from','availability_to','additional_notes','image',
        'reviews','complaints_customer','service_provider','provider_detail','service','invoice','complaints_provider']

    def get_customer_profile_img(self,instance):
        try:
            customer_profile_img = Customer.objects.get(user = instance.customer_id)
            return CustomerProfileImageSerializer(customer_profile_img).data
        except Customer.DoesNotExist:
            return None
   
    def get_reviews(self, instance):
        reviews = CustomerReview.objects.filter(service_request = instance.id)
        return ReviewDetailSerializer(reviews,many=True).data
        # serialized_reviews = ReviewSerializer(reviews,many=True).data
        # for review_data in serialized_reviews:
        #     customer = review_data.get('customer')
        #     if customer:
        #         customer_obj = Customer.objects.get(user = customer['id'])
        #         customer_serializer = CustomerSerializer(customer_obj)
        #         review_data['customer_profile_image'] = customer_serializer.data.get('profile_image')
        # return serialized_reviews
        
    def get_complaints_customer(self,instance):
        complaints_customer=Complaint.objects.filter(service_request=instance.id,sender=instance.customer_id,receiver=instance.service_provider_id)
        return ComplaintDetailSerializer(complaints_customer,many=True).data

    def get_provider_detail(self,instance):
        try:
            provider_detail = ServiceProvider.objects.get(id=instance.service_provider_id)
            return ServiceProviderProfileImageSerializer(provider_detail).data
        except ServiceProvider.DoesNotExist:
            return None
          
    def get_invoice(self,instance):
        try:
            invoice = Invoice.objects.get(service_request = instance.id)
            return InvoiceDetailSerializer(invoice).data
        except Invoice.DoesNotExist:
            return None
       
    def get_complaints_provider(self,instance):
        complaints_provider=Complaint.objects.filter(service_request=instance.id,sender=instance.service_provider_id,receiver=instance.customer_id)
        return ComplaintDetailSerializer(complaints_provider,many=True).data

    
from rest_framework import serializers
from Accounts.models import Customer,User,ServiceRequest,Complaint,Payment,Ad_Management


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id','full_name', 'address', 'landmark', 'pin_code', 'district', 
            'state', 'watsapp', 'email', 'phone_number', 'country_code', 
            'is_customer','password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ['user', 'profile_image', 'date_of_birth', 'gender','status']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password=user_data.get('password')
        user = User.objects.create(**user_data)
        user.set_password(password)
        user.save()
        customer = Customer.objects.create(user=user, **validated_data)
        return customer
    

class BookingSerializer(serializers.ModelSerializer):
    service_provider_name=serializers.CharField(source='service_provider.full_name')
    customer_name=serializers.CharField(source='customer.full_name')
    class Meta:
        model=ServiceRequest
        fields=['booking_id','service_provider','service_provider_name','customer','customer_name']

class ComplaintSerializer(serializers.ModelSerializer):
    sender_name=serializers.CharField(source='sender.full_name')
    class Meta:
        model=Complaint
        fields=['id','sender_name','status']


class AdsManagementSerializer(serializers.ModelSerializer):
    total_views=serializers.IntegerField(source='ad_category.total_views', read_only=True) 
    total_hits=serializers.IntegerField(source='ad_category.total_hits', read_only=True)
    ad_category=serializers.CharField(source='ad_category.ad_type',read_only=True)
    class Meta:
        model=Ad_Management
        fields = [ 'ad_id', 
                  'title', 'ad_category', 
                  'total_views','total_hits' ]
# serializers.py
from rest_framework import serializers
from Accounts.models import Franchisee, Franchise_Type, Category


class FranchiseeSerializer(serializers.ModelSerializer):
    franchisee_type = serializers.StringRelatedField(source='type.name')  # To show franchisee type name instead of ID

    class Meta:
        model = Franchisee
        fields = '__all__'  # Or you can specify fields like ['custom_id', 'user', 'status', 'valid_from', 'franchisee_type']
from rest_framework import serializers
from Accounts.models import Franchisee, Franchise_Type

class FranchiseeSerializer(serializers.ModelSerializer):
    # Custom field to display username or franchisee name
    franchisee_name = serializers.CharField(source='user.full_name', read_only=True)  
    franchisee_type = serializers.StringRelatedField(source='type.name')  # To show franchisee type name instead of ID

    class Meta:
        model = Franchisee
        fields = '__all__' 


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

