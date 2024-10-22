from datetime import datetime
import random
import re
from rest_framework import serializers
from Accounts.models import Customer, User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from Accounts.models import ServiceRequest, Customer, Subcategory
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
        fields = ['user','date_of_birth','gender','profile_image']


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


