from rest_framework import serializers
from Accounts.models import User, Franchisee
from django.db import models

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone_number', 'password','landmark','address','district','state','watsapp','country_code','pin_code']

    def create(self, validated_data):
        user = User(
            email=validated_data.get('email'),
            full_name=validated_data.get('full_name'),
            phone_number=validated_data.get('phone_number'),
            landmark=validated_data.get('landmark'),
            address=validated_data.get('address'),
            district=validated_data.get('district'),
            state=validated_data.get('state'),
            watsapp=validated_data.get('watsapp'),
            country_code=validated_data.get('country_code'),
            pin_code=validated_data.get('pin_code'),
            )
        
        user.set_password(validated_data.get('password'))  
        user.save()
        return user


class FranchiseeSerializer(serializers.ModelSerializer):
    
    user = UserSerializer() 

    class Meta:
        model = Franchisee
        fields = ['about', 'revenue', 'dealers', 'service_providers', 'type', 'valid_from', 
                  'valid_up_to', 'status', 'verification_id', 'verificationid_number', 'community_name', 'user']

    def create(self, validated_data):
        user_data = validated_data.pop('user')  
        user = UserSerializer.create(UserSerializer(), validated_data=user_data,) 
        user.is_franchisee = True
        user.save()
        franchisee = Franchisee.objects.create(user=user,**validated_data) 
        return franchisee

    def update(self, instance, validated_data):

        user_data = validated_data.pop('user', None)

        instance.about = validated_data.get('about', instance.about)
        instance.revenue = validated_data.get('revenue', instance.revenue)
        instance.dealers = validated_data.get('dealers', instance.dealers)
        instance.service_providers = validated_data.get('service_providers', instance.service_providers)
        instance.type = validated_data.get('type', instance.type)
        instance.valid_from = validated_data.get('valid_from', instance.valid_from)
        instance.valid_up_to = validated_data.get('valid_up_to', instance.valid_up_to)
        instance.status = validated_data.get('status', instance.status)
        instance.verification_id = validated_data.get('verification_id', instance.verification_id)
        instance.verificationid_number = validated_data.get('verificationid_number', instance.verificationid_number)
        instance.community_name = validated_data.get('community_name', instance.community_name)
        instance.save()

        if user_data:
            user = instance.user
            user.email = user_data.get('email', user.email)
            user.full_name = user_data.get('full_name', user.full_name)
            user.phone_number = user_data.get('phone_number', user.phone_number)
            user.landmark = user_data.get('landmark', user.landmark)
            user.address = user_data.get('address', user.address)
            user.district = user_data.get('district', user.district)
            user.state = user_data.get('state', user.state)
            user.watsapp = user_data.get('watsapp', user.watsapp)
            user.country_code = user_data.get('country_code', user.country_code)
            user.pin_code = user_data.get('pin_code', user.pin_code)

            if user_data.get('password'):
                user.set_password(user_data['password'])

            user.save()

        return instance