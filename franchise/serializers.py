from rest_framework import serializers
from Accounts.models import Dealer,Franchisee,User
from django.contrib.auth import authenticate


class FranchiseeLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
            
            try:
                franchisee = Franchisee.objects.get(user=user)
            except Franchisee.DoesNotExist:
                raise serializers.ValidationError('No associated franchisee account found.')
            
            if franchisee.status != 'Active':
                raise serializers.ValidationError('Franchisee account is not active.')
            
            data['user'] = user
            data['franchisee'] = franchisee
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        return data
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
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
        read_only_fields=['id','email']

class DealerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    franchise_name = serializers.CharField(source='franchisee.user.full_name', read_only=True)

    class Meta:
        model = Dealer
        fields = [
            'user',
            'custom_id',
            'about',
            'profile_image',
            'service_providers',
            'franchisee',
            'franchise_name',
            'status',
            'verification_id',
            'verificationid_number',
            'id_copy'
        ]
        read_only_fields = ['custom_id']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user

        # Check for unique email
        if User.objects.filter(email=user_data.get('email')).exclude(id=user.id).exists():
            user_data.pop('email')
            

        # Update user fields
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # Update Dealer fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
