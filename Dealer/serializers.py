from rest_framework import serializers
<<<<<<< HEAD
from Accounts.models import ServiceProviderVerification

=======
>>>>>>> f568851c93265555359d959eef8979965dcd140b
from django.contrib.auth import authenticate
from Accounts.models import *

class DealerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if user is None or not user.is_dealer:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Email and password are required.")

        attrs['user'] = user
<<<<<<< HEAD
        return attrs

class ServiceProviderVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProviderVerification
        fields = '__all__'
=======
        return attrs
>>>>>>> f568851c93265555359d959eef8979965dcd140b
