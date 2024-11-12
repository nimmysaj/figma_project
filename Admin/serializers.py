from rest_framework import serializers
from Accounts.models import Customer,User,ServiceRequest,Complaint,Payment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id','full_name', 'address', 'landmark', 'pin_code', 'district', 
            'state', 'watsapp', 'email', 'phone_number', 'country_code', 
            'is_customer','password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ['user', 'profile_image', 'date_of_birth', 'gender','status']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password=user_data.get('password')
        user = User.objects.create(**user_data)
        user.set_password(password)
        user.save()
        customer = Customer.objects.create(user=user, **validated_data)
        return customer
    

class BookingSerializer(serializers.ModelSerializer):
    service_provider_name=serializers.CharField(source='service_provider.full_name')
    customer_name=serializers.CharField(source='customer.full_name')
    class Meta:
        model=ServiceRequest
        fields=['booking_id','service_provider','service_provider_name','customer','customer_name']

class ComplaintSerializer(serializers.ModelSerializer):
    sender_name=serializers.CharField(source='sender.full_name')
    class Meta:
        model=Complaint
        fields=['id','sender_name','status']
