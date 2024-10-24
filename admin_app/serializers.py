from rest_framework import serializers
from Accounts.models import User,Franchisee,Franchise_Type,Country_Codes
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
import re  # For regex validation
import phonenumbers
from phonenumbers import NumberParseException



class UserSerializer(serializers.ModelSerializer):
    phone_with_code = serializers.SerializerMethodField() # New field to combine phone number and country code

    
    class Meta:
        model = User
        fields = [
            'id','last_login','is_customer','is_service_provider','is_franchisee','is_dealer','is_active','is_superuser',
            'is_staff','full_name','address','landmark','pin_code','nationality','designation','watsapp','email','phone_number',
            'country_code','phone_with_code',  'district','state','groups','user_permissions',
        ]
        # Exclude phone_number and country_code from the response
        extra_kwargs = {
            'country_code': {'write_only': True,'read_only':False},
            'phone_number': {'write_only': True,'read_only':False},  
        }
     

    def validate_full_name(self, value):
        if not value:
            raise serializers.ValidationError("Full name is required.")
        if len(value) < 3:
            raise serializers.ValidationError("Full name must be at least 3 characters long.")
        return value

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise serializers.ValidationError("Enter a valid email address.")
        return value


    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Password is required.")
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

    def validate_whatsapp(self, value):
        if not value:
            raise serializers.ValidationError("WhatsApp number is required.")
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Enter a valid WhatsApp number (10 digits).")
        return value


    def validate_pin_code(self, value):
        if not value:
            raise serializers.ValidationError("Pin code is required.")
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Enter a valid 6-digit pin code.")
        return value
    
    

    def validate_phone_number(self, value):
        """
        Validate the phone number with the country code, if provided.
        """
        if not value:
            raise serializers.ValidationError("Phone number is required.")

        if not value.isdigit() or len(value) < 9 or len(value) > 15:
            raise serializers.ValidationError("Phone number must be between 9 and 15 digits and numeric.")

        # If country code is provided, validate the full number
        country_code = self.initial_data.get('country_code')

        if country_code:
            try:
                # Fetch country code object
                country_obj = Country_Codes.objects.get(id=country_code)
                full_number = f"{country_obj.calling_code}{value}"
                
                # Parse the phone number
                parsed_number = phonenumbers.parse(full_number, None)
                print(country_obj)
                print(country_obj)
                print(full_number)
                
                # Check if the phone number is valid
                if not phonenumbers.is_valid_number(parsed_number):
                    raise serializers.ValidationError("Invalid phone number.")
            except Country_Codes.DoesNotExist:
                raise serializers.ValidationError("Invalid country code.")
            except NumberParseException:
                raise serializers.ValidationError("Phone number format is incorrect.")

        return value

    def get_phone_with_code(self, obj):
        """
        Combine phone number with country code for display.
        """
        if obj.phone_number and obj.country_code:
            return f"{obj.country_code.calling_code}{obj.phone_number}"
        return obj.phone_number  # Return just the phone number if country code is not provided


class FranchiseeSerializer(serializers.ModelSerializer):
    is_franchisee = serializers.CharField(source='user.is_franchisee')  
    location = serializers.CharField(source='user.district')  
    contact = serializers.CharField(source='user.phone_number')  
    dealers = serializers.IntegerField(read_only=True)  
    class Meta:
        model = Franchisee
        fields = [
            'is_franchisee',  
            'custom_id',       
            'revenue', 
            'dealers',          
            'service_providers',
            'location',        
            'contact',          
            'valid_up_to',     
            'status'            
        ]
class FranchiseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Franchise_Type
        fields = ['id', 'name', 'details', 'amount', 'currency']