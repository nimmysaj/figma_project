# serializers.py
from rest_framework import serializers
from Accounts.models import ServiceProvider, User
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


class FranchiseeRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()  # The email will be part of the user model
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
       validated_data['is_franchisee'] = True
       user = User(**validated_data)

       user.set_password(validated_data['password'])
       user.save()
       return user
    




# class FranchiseeLoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         email = data.get('email')
#         password = data.get('password')
#         user = authenticate(email=email,password=password)
        
#         # Authenticate user
#         # user = authenticate(request=self.context.get('request'), email=email, password=password)        
#         if user is None:
#             raise serializers.ValidationError("Invalid credentials")
        
#         # Check if user is a franchisee
#         if not user.is_franchisee:
#             raise serializers.ValidationError("User is not a franchisee")
        
#         refresh = RefreshToken.for_user(user)

        
#         return {
#             'user': user,
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#         }

User = get_user_model()

class FranchiseeLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request=self.context.get('request'), email=email, password=password)


        # Authenticate user using email and password
        # user = authenticate(request=self.context.get('request'), email=email, password=password)
        
        if user is None:
            raise serializers.ValidationError("Invalid credentials")

        # Check if the user is a franchisee (optional, based on your model)
        if not user.is_franchisee:
            raise serializers.ValidationError("User is not a franchisee")

        return {'user': user}
    
User = get_user_model()
   
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone_number', 'password']  # Include all necessary fields
        extra_kwargs = {'password': {'write_only': True}}  # Ensure password is write-only

    def create(self, validated_data):
        # Create the user instance with a hashed password
        user = User(
            email=validated_data['email'],
            full_name=validated_data.get('full_name', ''),
            phone_number=validated_data.get('phone_number', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# ServiceProviderSerializer with UserSerializer as a nested serializer


class ServiceProviderSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Use UserSerializer for nested user creation

    class Meta:
        model = ServiceProvider
        fields = '__all__'

    def create(self, validated_data):
        # Extract user data to create a User instance
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        
        # Validate and save the user
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()
        else:
            raise serializers.ValidationError({"error":"User creation failed"})
        
        # Automatically set the franchisee to the logged-in user (context)
        franchisee = self.context['request'].user

        validated_data.pop('franchisee', None)


        # Create and return the ServiceProvider instance linked to the user and franchisee
        try:
            service_provider = ServiceProvider.objects.create(
                user=user,
                franchisee=franchisee,
                **validated_data  # Any additional ServiceProvider fields
            )
            print("ServiceProvider created:", service_provider)
            return service_provider
        except Exception as e:
            print("Error creating ServiceProvider:", e)
            raise serializers.ValidationError({"error": "ServiceProvider creation failed."})