from rest_framework import serializers
from Accounts.models import Complaint, ServiceRegister, Collar, Category, Subcategory, User

class ServiceRegisterSerializer(serializers.ModelSerializer):
    available_lead_balance = serializers.SerializerMethodField(read_only=True)
    collar_amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ServiceRegister
        fields = ['id', 'service_provider', 'description', 'gstcode', 'category', 'subcategory', 'license', 
                  'status', 'image', 'accepted_terms', 'available_lead_balance', 'collar_amount']
        read_only_fields = ['available_lead_balance', 'collar_amount']

    def get_available_lead_balance(self, obj):
        if obj.subcategory and obj.subcategory.service_type.name == 'Daily Work':
            return 0  # For 'Daily Work', the lead balance is always 0.
        elif obj.subcategory and obj.subcategory.service_type.name == 'One Time Lead':
            if obj.subcategory.collar:
                # If available_lead_balance is None, return the collar's lead balance, else return the saved balance.
                return obj.update_lead_balance(0)
            return 0  # Return 0 if collar is missing.
        return None

    def get_collar_amount(self, obj):
        if obj.subcategory.service_type.name == 'Daily Work':
            return obj.subcategory.collar.amount
        elif obj.subcategory.service_type.name == 'One Time Lead' and obj.subcategory.collar:
            return obj.subcategory.collar.amount
        return None

    def create(self, validated_data):
        # Remove fields that are not part of the actual model
        validated_data.pop('available_lead_balance', None)
        validated_data.pop('collar_amount', None)

        # Now create the instance using the cleaned validated_data
        return super().create(validated_data)

    def validate(self, data):
        service_provider = data.get('service_provider')

        subcategory = None
        if 'subcategory' in data:
            subcategory = Subcategory.objects.get(id=data['subcategory'].id)

    # Check if the service provider is approved by the dealer

        # Check if the service provider is approved by the dealer
        if service_provider.verification_by_dealer != 'APPROVED':
            raise serializers.ValidationError("Service provider must be approved by the dealer to register the service.")

        # Ensure the service provider cannot register the same service multiple times
        if self.instance:
            if ServiceRegister.objects.filter(service_provider=service_provider, subcategory=subcategory).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Service provider has already registered this service.")
        else:
            if ServiceRegister.objects.filter(service_provider=service_provider, subcategory=subcategory).exists():
                raise serializers.ValidationError("Service provider has already registered this service.")

        # Validate "One Time Lead" requires collar
        if subcategory:
            if subcategory.service_type.name == "One Time Lead" and not subcategory.collar:
                raise serializers.ValidationError("Collar is required for One Time Lead services.")

        # Validate that `accepted_terms` is True
        if not data.get('accepted_terms', False):
            raise serializers.ValidationError("You must accept the terms and conditions to register the service.")

        return data
    
class ServiceRegisterUpdateSerializer(serializers.ModelSerializer):
    available_lead_balance = serializers.SerializerMethodField(read_only=True)
    collar_amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ServiceRegister
        fields = ['id', 'service_provider', 'description', 'gstcode', 'category', 'subcategory', 'license', 
                  'status', 'image', 'accepted_terms', 'available_lead_balance', 'collar_amount']
        read_only_fields = ['available_lead_balance', 'collar_amount']

    def get_available_lead_balance(self, obj):
        if obj.subcategory and obj.subcategory.service_type.name == 'Daily Work':
            return 0  # For 'Daily Work', the lead balance is always 0.
        elif obj.subcategory and obj.subcategory.service_type.name == 'One Time Lead':
            if obj.subcategory.collar:
                # If available_lead_balance is None, return the collar's lead balance, else return the saved balance.
                return obj.available_lead_balance
            return 0  # Return 0 if collar is missing.
        return None

    def get_collar_amount(self, obj):
        if obj.subcategory.service_type.name == 'Daily Work':
            return obj.subcategory.collar.amount
        elif obj.subcategory.service_type.name == 'One Time Lead' and obj.subcategory.collar:
            return obj.subcategory.collar.amount
        return None

    def create(self, validated_data):
        # Remove fields that are not part of the actual model
        validated_data.pop('available_lead_balance', None)
        validated_data.pop('collar_amount', None)

        # Now create the instance using the cleaned validated_data
        return super().create(validated_data)

    def validate(self, data):
        service_provider = data.get('service_provider')

        subcategory = None
        if 'subcategory' in data:
            subcategory = Subcategory.objects.get(id=data['subcategory'].id)

    # Check if the service provider is approved by the dealer

        # Check if the service provider is approved by the dealer
        if service_provider.verification_by_dealer != 'APPROVED':
            raise serializers.ValidationError("Service provider must be approved by the dealer to register the service.")

        # Ensure the service provider cannot register the same service multiple times
        if self.instance:
            if ServiceRegister.objects.filter(service_provider=service_provider, subcategory=subcategory).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Service provider has already registered this service.")
        else:
            if ServiceRegister.objects.filter(service_provider=service_provider, subcategory=subcategory).exists():
                raise serializers.ValidationError("Service provider has already registered this service.")

        # Validate "One Time Lead" requires collar
        if subcategory:
            if subcategory.service_type.name == "One Time Lead" and not subcategory.collar:
                raise serializers.ValidationError("Collar is required for One Time Lead services.")

        # Validate that `accepted_terms` is True
        if not data.get('accepted_terms', False):
            raise serializers.ValidationError("You must accept the terms and conditions to register the service.")

        return data


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            'id', 
            'customer', 
            'service_provider', 
            'service_request', 
            'subject', 
            'description', 
            'images', 
            'submitted_at', 
            'status', 
            'resolved_at', 
            'resolution_notes'
        ]
        read_only_fields = ['submitted_at', 'resolved_at', 'status', 'resolution_notes']

