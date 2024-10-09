from rest_framework import serializers
from Accounts.models import ServiceProvider, User



from rest_framework.exceptions import ValidationError

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

    # def create(self, validated_data):
    #     # Extract the nested user data from the validated data
    #     user_data = validated_data.pop('user')
        
    #     # Check if accepted_terms is False
    #     if not validated_data.get('accepted_terms'):
    #         raise ValidationError({"accepted_terms": "You must accept the terms and conditions to create a profile."})
        
        
    #     user = User.objects.create(**user_data)
        
    #     # Create the service provider profile
    #     service_provider = ServiceProvider.objects.create(user=user, **validated_data)
    #     return service_provider

    # def update(self, instance, validated_data):

    #     user_data = validated_data.pop('user', None)

      
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)

        
    #     if user_data:
    #         user = instance.user
    #         for attr, value in user_data.items():
    #             setattr(user, attr, value)
    #         user.save()

        
    #     instance.save()
    #     return instance

    def create(self, validated_data):
        # Extract the nested user data from the validated data
        user_data = validated_data.pop('user')

	 # Check if accepted_terms is False
        if not validated_data.get('accepted_terms'):
            raise ValidationError({"accepted_terms": "You must accept the terms and conditions to create a profile."})
        
        
        user = User.objects.create(**user_data)
        service_provider = ServiceProvider.objects.create(user=user, **validated_data)
        return service_provider

    def update(self, instance, validated_data):
        # Extract user data and handle separately
        user_data = validated_data.pop('user', None)

        # Update ServiceProvider fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle User fields separately
        if user_data:
            user = instance.user  # Get the related user instance
            for attr, value in user_data.items():
                if attr == 'email' and user.email:
                    continue  # Skip updating email if it's already set
                if attr == 'phone_number' and user.phone_number:
                    continue  # Skip updating phone number if it's already set
                setattr(user, attr, value)
            user.save()

        # Save the ServiceProvider instance with updated data
        instance.save()
        return instance

































# class UserSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = User
#         fields = [
#             'full_name',
#             'address', 
#             'landmark',
#             'pin_code',
#             'district',
#             'state',
#             'watsapp',
#             'email',
#             'phone_number', 
#             'country_code',
#             'is_customer',
#             'is_service_provider',
#             'is_franchisee',
#             'is_dealer'
#         ]

# class ServiceProviderSerialzer(serializers.ModelSerializer):
#     user = UserSerializer()

#     class Meta:
#         model = ServiceProvider
#         fields = "__all__"

#     def create(self, validated_data):
#         # Extract the nested user data from the validated data
#         user_data = validated_data.pop('user')  
#         user = User.objects.create(**user_data) 
#         service_provider = ServiceProvider.objects.create(user=user, **validated_data)
#         return service_provider
    
#     def update(self, instance, validated_data):
#         # Extract user data and handle separately
#         user_data = validated_data.pop('user', None)

#         # Update ServiceProvider fields
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         # If user data is provided, update the related User instance
#         if user_data:
#             user = instance.user 
#             for attr, value in user_data.items():
#                 setattr(user, attr, value)
#             user.save() 

#         # Save the ServiceProvider instance with updated data
#         instance.save()
#         return instance

