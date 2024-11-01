
# serializers.py

from rest_framework import serializers
from django.contrib.auth import authenticate
from Accounts.models import *

class FranchiseeLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if user is None or not user.is_franchisee:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Email and password are required.")

        attrs['user'] = user
        return attrs
    

from rest_framework import serializers
from Accounts.models import ServiceProvider

class ServiceProviderSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = ServiceProvider
        fields = '__all__'  # Specify fields explicitly if needed

    def get_full_name(self, obj):
        return obj.user.full_name if obj.user else None

from rest_framework import serializers
from Accounts.models import ServiceProvider, ServiceRegister, CustomerReview

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRegister
        fields = '__all__'  # Or specify fields explicitly if needed

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerReview
        fields = '__all__'  # Or specify fields explicitly if needed


from rest_framework import serializers
from Accounts.models import Dealer

class DealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealer
        fields = '__all__'  # Or specify individual fields if needed



class ServiceRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRegister
        fields = ['service_provider', 'description', 'gstcode', 'category', 'subcategory', 'accepted_terms']

    def create(self, validated_data):
        # You can perform any additional validation or processing here
        return super().create(validated_data)

# class ServiceProviderSerializer(serializers.ModelSerializer):
#     # Custom fields to get information from related models
#     full_name = serializers.SerializerMethodField()
#     email = serializers.EmailField(source='user.email', read_only=True)

#     total_service_providers = serializers.SerializerMethodField()
#     approved_count = serializers.SerializerMethodField()
#     pending_count = serializers.SerializerMethodField()

#     class Meta:
#         model = ServiceProvider
#         fields = '__all__'  # Or specify fields explicitly if needed

#     def get_full_name(self, obj):
#         return obj.user.full_name if obj.user else None

#     def get_total_service_providers(self, obj):
#         dealer = self.context.get('dealer')  # Access dealer from context
#         return ServiceProvider.objects.filter(dealer=dealer).count()

#     def get_approved_count(self, obj):
#         dealer = self.context.get('dealer')  # Access dealer from context
#         return ServiceProvider.objects.filter(dealer=dealer, verification_by_dealer='APPROVED').count()

#     def get_pending_count(self, obj):
#         dealer = self.context.get('dealer')  # Access dealer from context
#         return ServiceProvider.objects.filter(dealer=dealer, verification_by_dealer='PENDING').count()


# class CreateServiceProviderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ServiceProvider
#         fields = [
#             'custom_id', 'profile_image', 'date_of_birth', 'gender',
#             'about', 'dealer', 'franchisee', 'address_proof_document', 
#             'id_number', 'address_proof_file', 'payout_required', 'status',
#             'verification_by_dealer', 'accepted_terms'
#         ]
#         read_only_fields = ['custom_id']  # custom_id will be generated automatically

#     def create(self, validated_data):
#         # Override verification_by_dealer to set it to False
#         validated_data['verification_by_dealer'] = False
#         return ServiceProvider.objects.create(**validated_data)

#     def create(self, validated_data):
#         # Override verification_by_dealer to set it to False
#         validated_data['verification_by_dealer'] = False
#         return ServiceProvider.objects.create(**validated_data)


# # dealer dashboard

# from rest_framework import serializers
# from Accounts.models import Franchisee, Franchise_Type

# class FranchiseTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Franchise_Type
#         fields = ['name', 'details', 'amount', 'currency']  # Include the fields you want from Franchise_Type

# class FranchiseSerializer(serializers.ModelSerializer):
#     type = FranchiseTypeSerializer()  # Nest FranchiseTypeSerializer to get franchise type details

#     class Meta:
#         model = Franchisee
#         fields = [
#             'custom_id',
#             'about',
#             'profile_image',
#             'revenue',
#             'dealers',
#             'service_providers',
#             'type',  # Include the nested FranchiseTypeSerializer here
#             'valid_from',
#             'valid_up_to',
#             'status',
#             'verification_id',
#             'verificationid_number',
#             'community_name',
#         ]


# class ServiceProviderAddSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ServiceProvider
#         fields = [
#             'user',
#             'profile_image',
#             'date_of_birth',
#             'gender',
#             'about',
#             'dealer',
#             'franchisee',
#             'address_proof_document',
#             'id_number',
#             'address_proof_file',
#             'payout_required',
#             'status',
#             'verification_by_dealer',
#             'accepted_terms',
#         ]



class AddDealerSerializer(serializers.ModelSerializer):
    # Fields for User model
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=True)
    full_name = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    pin_code = serializers.CharField(required=True)
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())
    
    # Fields for Dealer model
    about = serializers.CharField(required=True)
    profile_image = serializers.ImageField(required=False)
    service_providers = serializers.IntegerField(required=False)
    franchisee = serializers.PrimaryKeyRelatedField(queryset=Franchisee.objects.all())
    verification_id = serializers.CharField(required=False)
    verificationid_number = serializers.CharField(required=False)
    id_copy = serializers.FileField(required=False)

    class Meta:
        model = Dealer
        fields = ['email', 'phone_number', 'full_name', 'address', 'pin_code', 
                 'district', 'state', 'about', 'profile_image', 'service_providers',
                 'franchisee', 'verification_id', 'verificationid_number', 'id_copy']
        


class AddServiceProviderSerializer(serializers.ModelSerializer):
    # Fields for User model
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=True)
    full_name = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    pin_code = serializers.CharField(required=True)
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())
    
    # Fields for ServiceProvider model
    about = serializers.CharField(required=False)
    profile_image = serializers.ImageField(required=False)
    date_of_birth = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES)
    dealer = serializers.PrimaryKeyRelatedField(queryset=Dealer.objects.all())
    franchisee = serializers.PrimaryKeyRelatedField(queryset=Franchisee.objects.all())
    address_proof_document = serializers.CharField(required=False)
    id_number = serializers.CharField(required=False)
    address_proof_file = serializers.FileField(required=False)
    payout_required = serializers.ChoiceField(choices=ServiceProvider.PAYOUT_FREQUENCY_CHOICES)

    class Meta:
        model = ServiceProvider
        fields = ['email', 'phone_number', 'full_name', 'address', 'pin_code', 
                 'district', 'state', 'about', 'profile_image', 'date_of_birth',
                 'gender', 'dealer', 'franchisee', 'address_proof_document',
                 'id_number', 'address_proof_file', 'payout_required']
