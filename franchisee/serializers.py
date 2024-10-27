from rest_framework import serializers
import logging
import phonenumbers
from Accounts.models import *
from django_filters import rest_framework as filters

class ServiceProviderListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source= 'user.full_name')
    id = serializers.CharField()
    registered_services = serializers.IntegerField(source= 'services.count', read_only = True)
    active_jobs = serializers.SerializerMethodField()
    status = serializers.CharField()
    contacts = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(write_only= True)
    franchisee_profile = serializers.SerializerMethodField() 

    class Meta:
        model = ServiceProvider
        fields = ['name', 'id', 'registered_services', 'active_jobs', 'status', 'contacts', 'district', 'created_at', 'franchisee_profile']

    def get_contacts(self, obj):
        return{
            "phone_number": obj.user.phone_number,
            "email": obj.user.email
        }    
    def get_district(self, obj):
        return obj.user.district.name if obj.user.district else None
    
    def get_active_jobs(self, obj):
        return ServiceRequest.objects.filter(
            service_provider = obj.user,
            acceptance_status = "accept",
            work_status = 'in_progress'
        ).count()
    
    def get_franchisee_profile(self, obj):
        user = self.context.get('request').user
        franchisee = Franchisee.objects.get(user=user)
        return {
            "name": franchisee.user.full_name,
            "image": franchisee.profile_image.url
            if franchisee.profile_image
            else None,
            "title": "Franchisee"
        }
       
# franchise login    
logger = logging.getLogger(__name__)

class FranchiseLoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        password = attrs.get('password')

        if not email_or_phone:
            raise serializers.ValidationError('Email or phone is required.')
        if not password:
            raise serializers.ValidationError('Password is required.')

        user = None

        # Look up user by email or phone
        if '@' in email_or_phone:
            try:
                user = User.objects.get(email=email_or_phone)
                logger.debug(f"Found franchisee by email: {user.email}")
            except User.DoesNotExist:
                raise serializers.ValidationError('No account found with this email.')
        else:
            try:
                fullnumber = phonenumbers.parse(email_or_phone, None)
                code = Country_Codes.objects.get(calling_code="+" + str(fullnumber.country_code))
                number = str(fullnumber.national_number)
                
                user = User.objects.get(phone_number=number, country_code=code)
                logger.debug(f"Found franchisee by phone: {user.email}")
            except (phonenumbers.phonenumberutil.NumberParseException, Country_Codes.DoesNotExist):
                raise serializers.ValidationError('Invalid phone number format.')
            except User.DoesNotExist:
                raise serializers.ValidationError('No account found with this phone number.')

        # Validate franchisee status
        if not user.is_active:
            raise serializers.ValidationError('This account is inactive.')
        if not user.is_franchisee:
            raise serializers.ValidationError('This account is not registered as a franchisee.')

        # Check password
        if not user.check_password(password):
            logger.debug(f"Password verification failed for franchisee: {user.email}")
            raise serializers.ValidationError('Invalid password.')

        logger.debug("Franchisee authentication successful.")
        attrs['user'] = user
        return attrs