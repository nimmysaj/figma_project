import re
from rest_framework import serializers
from Accounts.models import Customer, User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password



class UserSerializer(serializers.ModelSerializer):
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
        profile_data = validated_data.pop('user')    #extract customer data
        user = User.objects.create(**profile_data)   #create user
        user.is_customer = True                      #Ensure user is marked as a customer
        user.save()

        customer = Customer.objects.create(user=user, **validated_data)   #create customer data associated with that user
        return customer




    
