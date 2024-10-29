from rest_framework import serializers
from django.contrib.auth import authenticate



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