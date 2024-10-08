from rest_framework import serializers
from Accounts.models import ServiceProvider, User, Payment, Invoice


# ----------------------------------------------------------- PAYMENT ---------------------------------------------------------------------


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'




# ----------------------------------------------------------- PROFILE ---------------------------------------------------------------------


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
            'phone_number', 
            'country_code',
            'is_customer',
            'is_service_provider',
            'is_franchisee',
            'is_dealer'
        ]

class ServiceProviderSerialzer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ServiceProvider
        fields = "__all__"

    def create(self, validated_data):
        # Extract the nested user data from the validated data
        user_data = validated_data.pop('user')  
        user = User.objects.create(**user_data) 
        service_provider = ServiceProvider.objects.create(user=user, **validated_data)
        return service_provider
    
    def update(self, instance, validated_data):
        # Extract user data and handle separately
        user_data = validated_data.pop('user', None)

        # Update ServiceProvider fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If user data is provided, update the related User instance
        if user_data:
            user = instance.user 
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save() 

        # Save the ServiceProvider instance with updated data
        instance.save()
        return instance
    


