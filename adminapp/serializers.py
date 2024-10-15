from datetime import datetime
import random
import re
import uuid
from rest_framework import serializers
from Accounts.models import Customer, User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.db import transaction



class UserSerializer(serializers.ModelSerializer):   # serializers.ModelSerializer - parent cls of UserSerializer 
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User 
        fields = ['full_name','address','landmark','pin_code','district','state','watsapp','email','phone_number','country_code','password']
    
    
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

        # # Use Django's built-in password validators.
        # validate_password(value)
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

        # with transaction.atomic():
        #     try:
        #         # create user instance
        #         user = User.objects.create(**profile_data)   #create user (**profile_data) 
        #         user.is_customer = True                      #Ensure user is marked as a customer
        #         user.save()


        #         # Generate custom_id like 'USER20241014' + random number
        #         current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        #         randum_number = random.randint(100,999)
        #         custom_id = f"USER{current_time}{randum_number}"

        #         # create customer instance
        #         customer = Customer.objects.create(user=user, custom_id=custom_id, **validated_data)
            
        #     except Exception as e:
        #         # If any part of the process fails, the whole transaction will be rolled back 
        #         raise serializers.ValidationError(f"Error creating customer: {str(e)}")
        #     return customer


        # custom_id = str(uuid.uuid4())
        customer = Customer.objects.create(user=user, **validated_data)   #create customer data associated with that user
        return customer

