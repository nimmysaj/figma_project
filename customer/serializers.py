import re
from django.contrib.auth import get_user_model
import phonenumbers
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from Accounts.models import Category, Country_Codes, Customer, CustomerReview, Invoice, ServiceProvider, ServiceRegister, ServiceRequest, Subcategory
from django.contrib.auth.password_validation import validate_password
from django.db.models import Avg
from django.core.validators import validate_email
from rest_framework.exceptions import ValidationError

User = get_user_model()

#registration and otp verification
class RegisterSerializer(serializers.ModelSerializer):
    email_or_phone = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    
    
    class Meta:
        model = User
        fields = ['email_or_phone', 'password', 'confirm_password']
    
    def validate_new_password(self, value):
        # Use Django's built-in password validators to validate the password
        validate_password(value)

        # Custom validation for password complexity
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")

        return value

    def validate(self, data):
        email_or_phone = data.get('email_or_phone')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Check if both passwords match
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")

        # Validate email or phone number format
        if '@' in email_or_phone:
            # Check if email is already registered
            validate_email(email_or_phone)
            if User.objects.filter(email=email_or_phone).exists():
                raise serializers.ValidationError("Email is already in use")
        else:
            # Check if phone number is already registered
            #if User.objects.filter(phone_number=email_or_phone).exists():
            try:
                parsed_number = phonenumbers.parse(email_or_phone, None)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise ValidationError("Invalid phone number.")
            except phonenumbers.NumberParseException:
                raise ValidationError("Invalid phone number format.")

            fullnumber=phonenumbers.parse(email_or_phone,None)
            try:
                code=Country_Codes.objects.get(calling_code="+"+str(fullnumber.country_code))
            except Country_Codes.DoesNotExist:
                raise serializers.ValidationError("Can't idntify country code")
            if User.objects.filter(phone_number=str(fullnumber.national_number),country_code=code).exists():    
                raise serializers.ValidationError("Phone number is already in use")

        return data

    def create(self, validated_data):
        email_or_phone = validated_data.get('email_or_phone')
        password = validated_data.get('password')

        # Create user based on whether email or phone is provided
        if '@' in email_or_phone:
            #user = User.objects.create_user(email=email_or_phone, password=password)
            user = User.objects.create(email=email_or_phone)
        else:
            #user = User.objects.create_user(phone_number=email_or_phone, password=password)
            fullnumber=phonenumbers.parse(email_or_phone,None)
            code=Country_Codes.objects.get(calling_code="+"+str(fullnumber.country_code))
            number=str(fullnumber.national_number)
            user = User.objects.create(country_code=code,phone_number=number)
        
        user.set_password(password)
        # Ensure that is_customer is always set to True during registration
        user.is_active = False  # User is inactive until OTP is verified
        user.is_customer = True
        user.save()

        if user.is_customer:
            Customer.objects.create(user=user)

        return user
    
class ResendOTPSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True)

    def validate(self, data):
        email_or_phone = data.get('email_or_phone')

        # Check if the user exists with either email or phone
        if '@' in email_or_phone:
            if not User.objects.filter(email=email_or_phone).exists():
                raise serializers.ValidationError("User with this email does not exist.")
        else:
            try:
                parsed_number = phonenumbers.parse(email_or_phone, None)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise ValidationError("Invalid phone number.")
            except phonenumbers.NumberParseException:
                raise ValidationError("Invalid phone number format.")

            fullnumber=phonenumbers.parse(email_or_phone,None)
            try:
                code=Country_Codes.objects.get(calling_code="+"+str(fullnumber.country_code))
            except Country_Codes.DoesNotExist:
                raise serializers.ValidationError("Can't idntify country code")
            if not User.objects.filter(phone_number=str(fullnumber.national_number),country_code=code).exists():
            #if not User.objects.filter(phone_number=email_or_phone).exists():
                raise serializers.ValidationError("User with this phone number does not exist.")

        return data

    def get_user(self):
        email_or_phone = self.validated_data['email_or_phone']
        if '@' in email_or_phone:
            return User.objects.get(email=email_or_phone)
        else:
            return User.objects.get(phone_number=email_or_phone)

#login customer
class CustomerLoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        password = attrs.get('password')

        # Validate that either email or phone and password are provided
        if not email_or_phone:
            raise serializers.ValidationError('Email or phone is required.')
        if not password:
            raise serializers.ValidationError('Password is required.')

        # Try to authenticate the user using email or phone number
        user = None
        if '@' in email_or_phone:
            # If input is email
            user = authenticate(username=email_or_phone, password=password)
        else:
            # If input is phone number
            try:
                #user = User.objects.get(phone_number=email_or_phone)
                fullnumber=phonenumbers.parse(email_or_phone,None)
                code=Country_Codes.objects.get(calling_code="+"+str(fullnumber.country_code))
                number=str(fullnumber.national_number)
                user = User.objects.get(phone_number=number,country_code=code)
                if not user.check_password(password):
                    raise serializers.ValidationError('Invalid credentials.')
            except phonenumbers.phonenumberutil.NumberParseException:
                raise serializers.ValidationError('Wrong phone number or email format')    
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid login credentials.')

        if user is None or not user.is_customer:
            raise serializers.ValidationError('Invalid login credentials or not a customer.')

        attrs['user'] = user
        return attrs    

#forgot password and set new pasword    
class CustomerPasswordForgotSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True)

    def validate_email_or_phone(self, value):
        """
        This function will check if the provided value is either a valid email or a phone number.
        For now, we assume the input is either an email or phone number.
        """
        if '@' in value:
            # Validate as email
            if not User.objects.filter(email=value, is_customer=True).exists():
                raise serializers.ValidationError("This email is not registered with any customer.")
        else:
            # Validate as phone number
            #if not User.objects.filter(phone_number=value, is_customer=True).exists():
            try:
                fullnumber=phonenumbers.parse(value,None)
                code=Country_Codes.objects.get(calling_code="+"+str(fullnumber.country_code))
                number=str(fullnumber.national_number)
            except phonenumbers.phonenumberutil.NumberParseException:
                raise serializers.ValidationError('Wrong phone number or email format')
            if not User.objects.filter(phone_number=number,country_code=code, is_customer=True).exists():
                raise serializers.ValidationError("This phone number is not registered with any customer.")

        return value    

class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate_password(self, value):
        # Use Django's password validators to validate the password
        validate_password(value)

        # Custom validation for password complexity
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")


        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    
#for profile creation of customers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'full_name',
            'address', 
            'landmark',
            'pin_code',
            'district',
            'state',
            'watsapp',
            'email',
            'country_code',
            'phone_number'
            ]
        
class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = [ "user",
            "profile_image",
            "date_of_birth",
            "gender" 
            ]

    def create(self, validated_data):
        # Extract the nested user data from the validated data
        user_data = validated_data.pop('user')
        
        # Check if accepted_terms is False
        if not validated_data.get('accepted_terms'):
            raise ValidationError({"accepted_terms": "You must accept the terms and conditions to create a profile."})

        user = User.objects.create(**user_data)
        customer = Customer.objects.create(user=user, **validated_data)
        return customer

    def update(self, instance, validated_data):
        # Extract user data and handle separately
        user_data = validated_data.pop('user', None)

        # Update customer fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle User fields separately
        if user_data:
            user = instance.user  # Get the related user instance
            for attr, value in user_data.items():
                if attr == 'email' and user.email:
                    continue  # Skip updating email if it's already set
                if attr == 'phone_number' and user.phone_number:
                    continue  # Skip updating phone number if it's already set
                setattr(user, attr, value)
            user.save()

        # Save the customer instance with updated data
        instance.save()
        return instance



#view category subcategory and service providers
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'image']

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'title', 'description', 'image']

class ServiceProviderSerializer(serializers.ModelSerializer):
     # Fetch the full name from the related User model
    full_name = serializers.CharField(source='user.full_name') 
    
    
    # Fetch the amount from the ServiceRegister model
    amount_forthis_service = serializers.SerializerMethodField()
    
    # Fetch the rating (assuming it's available in ServiceProvider or related models)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = ServiceProvider
        fields = ['id', 'full_name', 'profile_image','amount_forthis_service', 'rating']

    def get_amount_forthis_service(self, obj):
        return 0
          
    def get_rating(self, obj):
        # Get all reviews related to the service provider using the related name 'to_review'
        reviews = obj.user.to_review.all()
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            return total_rating / reviews.count()  # Calculate the average rating
        return None  # Return None if no reviews are present   
      

# For detailed view of service provider        
class CustomerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerReview
        fields = ['customer', 'rating', 'image', 'comment', 'created_at']

class ServiceRegisterSerializer(serializers.ModelSerializer):
    subcategory = serializers.CharField(source='subcategory.title')  # Use source to get the title instead of id

    class Meta:
        model = ServiceRegister
        fields = ['subcategory']  # Only include the field you want to display (e.g., subcategory.title)

class ServiceProviderProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name')
    address = serializers.CharField(source='user.address')
    landmark = serializers.CharField(source='user.landmark')
    pin_code = serializers.CharField(source='user.pin_code')
    district = serializers.CharField(source='user.district')
    state = serializers.CharField(source='user.state')
    about = serializers.CharField()
    work_history_completed = serializers.SerializerMethodField()  
    services = ServiceRegisterSerializer(many=True, read_only=True)  # Use the custom service serializer  
    reviews = CustomerReviewSerializer(many=True, source='user.to_review')  

    class Meta:
        model = ServiceProvider
        fields = ['full_name', 'address', 'landmark', 'pin_code', 'district', 'state', 'about','work_history_completed','services', 'reviews' ]

    def get_work_history_completed(self, obj):
        return ServiceRequest.objects.filter(service_provider=obj.user, work_status='completed').count()        
    


#for service request and request views
class ServiceRequestSerializer(serializers.ModelSerializer):
    subcategory_title = serializers.CharField(source='service.subcategory.title', read_only=True)
    subcategory_id = serializers.IntegerField(source='service.subcategory.id', read_only=True)  # Get subcategory ID
    #service_title = serializers.CharField(source='service.title', read_only=True)  # Get service title
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    service_provider_name = serializers.CharField(source='service_provider.full_name', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'customer_name',
            'service_provider_name',
            'service',  # Holds the service ID
            'title',  # Service title for output
            'subcategory_title',
            'subcategory_id',  # Subcategory ID for output
            'work_status',
            'acceptance_status',
            'availability_from',
            'availability_to',
            'additional_notes',
            'image',
            'booking_id',
           
        ]
        read_only_fields = ['booking_id', 'customer', 'service', 'title', 'subcategory_title', 'subcategory_id']

class ServiceRequestDetailSerializer(serializers.ModelSerializer):
    subcategory_name = serializers.CharField(source='service.subcategory.title', read_only=True)
    #service_title = serializers.CharField(source='service.title', read_only=True)  # Get service title
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'title',
            'subcategory_name',
            'customer_name',
            'availability_from',
            'availability_to',
            'acceptance_status'
        ]    
