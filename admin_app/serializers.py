from rest_framework import serializers
from Accounts.models import *
from django.core.validators import validate_email
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password 

# serializers.py


# TASK 1 Franchisee Registration ////////////////////////////////////////////////////////////////////////////////////

class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15, validators=[phone_regex])

    class Meta:
        model = User
        fields = [
            'email', 'phone_number', 'full_name', 'landmark', 'address',
            'district', 'state', 'watsapp', 'country_code', 'pin_code', 'password'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        # Skip uniqueness check if updating with the same email
        if self.instance and self.instance.email == value:
            return value
        # Otherwise, check if email exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_phone_number(self, value):
        # Skip uniqueness check if updating with the same phone number
        if self.instance and self.instance.phone_number == value:
            return value
        # Otherwise, check if phone number exists
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("User with this phone number already exists.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class FranchiseeSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nest the UserSerializer
    Amount_to_pay = serializers.SerializerMethodField() 
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), required=False)
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all(), required=False)
    country_code = serializers.PrimaryKeyRelatedField(queryset=Country_Codes.objects.all(), required=False)
    
    class Meta:
        model = Franchisee
        fields = [
            'user', 'custom_id', 'about', 'profile_image', 'revenue', 
            'dealers', 'service_providers', 'type', 'valid_from', 
            'valid_up_to', 'status', 'verification_id', 'verificationid_number', 
            'community_name', 'Amount_to_pay', 'district', 'state', 'country_code'
        ]

    def validate(self, data):
        valid_from = data.get('valid_from')
        valid_up_to = data.get('valid_up_to')

        if valid_from and valid_up_to and valid_up_to <= valid_from:
            raise serializers.ValidationError({
                "valid_up_to": "valid_up_to must be later than valid_from."
            })

        # Check custom_id uniqueness
        custom_id = data.get('custom_id')
        if custom_id and Franchisee.objects.filter(custom_id=custom_id).exists():
            raise serializers.ValidationError({
                "custom_id": "A franchisee with this custom_id already exists."
            })

        # Check non-negative values
        if data.get('revenue') is not None and data['revenue'] < 0:
            raise serializers.ValidationError({
                "revenue": "Revenue must be a non-negative value."
            })
        if data.get('dealers') is not None and data['dealers'] < 0:
            raise serializers.ValidationError({
                "dealers": "Dealers count must be a non-negative value."
            })
        if data.get('service_providers') is not None and data['service_providers'] < 0:
            raise serializers.ValidationError({
                "service_providers": "Service providers count must be a non-negative value."
            })

        # Check if type exists in Franchise_Type
        if not Franchise_Type.objects.filter(id=data.get('type').id).exists():
            raise serializers.ValidationError({
                "type": "The specified franchise type does not exist."
            })

        return data

    def get_Amount_to_pay(self, obj):
        # Example: assume type has a fixed amount to pay field
        if obj.type and obj.type.amount:
            return obj.type.amount
        return 0

    def create(self, validated_data):
        user_data = validated_data.pop('user')

        # Ensure email and phone_number are required for creation
        if 'email' not in user_data or 'phone_number' not in user_data:
            raise serializers.ValidationError("Both email and phone number are required to create a new franchisee.")
        
        user_data['is_franchisee'] = True
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        
        # Create the franchisee instance
        franchisee = Franchisee.objects.create(user=user, **validated_data)
        return franchisee

    def update(self, instance, validated_data):
        # Extract user data if provided
        user_data = validated_data.pop('user', None)

        # Update the user information if user_data is provided
        if user_data:
            # Check if password is being updated and hash it before saving
            password = user_data.get('password', None)
            if password:
                # If password is present in the update, hash it
                instance.user.set_password(password)  # Hash and set the password
                instance.user.save()

            # Update the other user fields
            for attr, value in user_data.items():
                if attr != 'password':  # Don't overwrite password here
                    setattr(instance.user, attr, value)
            instance.user.save()  # Save the user model after updates

        # Update the remaining franchisee fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()  # Save changes to the franchisee

        return instance
    
    
    
class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'invoice_type', 'description', 'price', 'total_amount', 'payment_status', 'accepted_terms', 'invoice_date']
# TASK 2 Transaction History ////////////////////////////////////////////////////////////////////////////////////
 
    
    
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['transaction_id', 'invoice', 'amount_paid',
                  'payment_method', 'payment_date', 'payment_status', 'sender', 'receiver']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Safely get the invoice type
        representation['type'] = getattr(instance.invoice, 'invoice_type', None)
        representation['description'] = getattr(instance.invoice, 'description', None)

        # Initialize sender to None
        sender = None
        if instance.sender.is_customer:
            try:
                # Fetch the Customer data using sender's user_id
                customerdata = Customer.objects.get(user_id=instance.sender.id)
                sender = customerdata.custom_id
            except Customer.DoesNotExist:
                sender = None  # If the customer does not exist, handle it gracefully

        elif instance.sender.is_franchisee:
            try:
                # Fetch the Franchisee data using sender's user_id
                franchiseedata = Franchisee.objects.get(user_id=instance.sender.id)
                sender = franchiseedata.custom_id
            except Franchisee.DoesNotExist:
                sender = None  # If the franchisee does not exist, handle it gracefully

        elif instance.sender.is_dealer:
            try:
                # Fetch the Dealer data using sender's user_id
                dealerdata = Dealer.objects.get(user_id=instance.sender.id)
                sender = dealerdata.custom_id
            except Dealer.DoesNotExist:
                sender = None  # If the dealer does not exist, handle it gracefully

        # Set the sender and receiver fields
        representation['sender'] = sender
        representation['receiver'] = instance.receiver.id

        return representation

# TASK 3 SERVICE TYPE CRUD //////////////////////////////////////////////////////////////////////////////////////////////////

class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service_Type
        fields = ['id', 'name', 'details', 'currency']
        
    def validate_name(self, value):
        """Ensure name uniqueness, except for the current instance."""
        service_id = self.instance.id if self.instance else None

        if Service_Type.objects.filter(name=value).exclude(id=service_id).exists():
            raise serializers.ValidationError("A service type with this name already exists.")
        
        return value
    
# TASK 3 Collor CRUD //////////////////////////////////////////////////////////////////////////////////////////////////

class CollarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collar
        fields = ['id', 'name', 'lead_quantity', 'amount']

    def validate_name(self, value):
        """Check for duplicate collar names."""
        # Allow the current instance's name to pass the validation during updates
        if self.instance and self.instance.name == value:
            return value
        if Collar.objects.filter(name=value).exists():
            raise serializers.ValidationError("A collar with this name already exists.")
        return value

    def update(self, instance, validated_data):
        """Update the Collar object."""
        instance.name = validated_data.get('name', instance.name)
        instance.lead_quantity = validated_data.get('lead_quantity', instance.lead_quantity)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance
    
    
    
    
# TASK 4 Ad category //////////////////////////////////////////////////////////////////////////////////////////////////

class AdCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad_category
        fields = '__all__'

    def validate_type(self, value):
        """Ensure that the same ad type cannot be posted more than once."""
        if self.instance:  # If this is an update
            # If the 'type' is unchanged, allow it
            if self.instance.type == value:
                return value

        # For both new and changed types, check for duplicates
        if Ad_category.objects.filter(type=value).exists():
            raise serializers.ValidationError(f"An Ad Category with type '{value}' already exists.")

        return value
    
    def validate_rate(self, value):
        """Ensure the rate is a positive value."""
        if value <= 0:
            raise serializers.ValidationError("Rate must be greater than zero.")
        return value
    
    
    def validate_status(self, value):
        """Ensure the status is either 'Active' or 'Inactive'."""
        if value not in ['Active', 'Inactive']:
            raise serializers.ValidationError("Status must be either 'Active' or 'Inactive'.")
        return value
        
    def validate(self, data):
        """Override the validate method to apply custom checks."""
        # Ensure image dimensions are valid
        image_width = data.get('image_width')
        image_height = data.get('image_height')
        
        # Check if image dimensions are less than 100px
        if image_width < 100 or image_height < 100:
            raise serializers.ValidationError("Image width and height should be greater than or equal to 100px.")
        
        return data

# TASK 5 ADD Expenses ////////////////////////////////////////////////////////////////////////////////////////

class AddExpensesSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=True, max_length=255)
    accepted_terms = serializers.BooleanField(required=True)
    invoice_type = serializers.CharField(default="others", read_only=True)  # Fixed to "others"
    income = serializers.DecimalField(max_digits=10, decimal_places=2,required= False, write_only=True)
    expense = serializers.DecimalField(max_digits=10, decimal_places=2,required=False, write_only=True)
    
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)



    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_type', 'invoice_date', 'sender', 'receiver',
            'description', 'invoice_document', 'accepted_terms','total_amount', 'payment_status','external_invoice_number',
            'income','expense'
        ]

    def validate_accepted_terms(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the terms to proceed.")
        return value
    

    def validate(self, data):
        
        admin_user = User.objects.filter(is_superuser=True).first()
        expense = data.pop('expense', None)
        income = data.pop('income', None)
        receiver = data.pop('receiver', None)
        sender = data.pop('sender', None)
        
        
        if not admin_user:
            raise serializers.ValidationError("Admin user not found.")
        
        if expense and income:
            raise serializers.ValidationError("Only one of Income or Expense should be provided.")
        
        if income :
            if income <= 0:
                raise serializers.ValidationError("Must be a positive value.")
            elif income >= 1:
                    data['receiver'] = admin_user 
                    data['sender'] = None 
                    data['total_amount'] = income
                
        elif expense:
            if expense <= 0:
                raise serializers.ValidationError("Must be a positive value.")
            elif expense >= 1:
                    data['sender'] = admin_user 
                    data['receiver'] = None
                    data['total_amount'] = expense
                    
        else:
            raise serializers.ValidationError("Either Income or Expense should be provided.")
                 
        return data
               

    def create(self, validated_data):
        validated_data['invoice_type'] = 'others'
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['invoice_type'] = 'others' 
        return super().update(instance, validated_data)