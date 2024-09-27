from rest_framework import serializers
from Accounts.models import ServiceProvider, User


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

# class ServiceProviderSerializer(serializers.ModelSerializer):
#     """
#     Serializer for the ServiceProvider model.
#     The `user` field is represented using the UserSerializer.
#     """
#     user = UserSerializer()  # Nested serializer to include user details

#     class Meta:
#         model = ServiceProvider
#         fields = [
#             'user',  # Nested UserSerializer
#             'profile_image',
#             'date_of_birth',
#             'gender',
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




class ServiceProviderSerialzer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ServiceProvider
        fields = "__all__"

    def create(self, validated_data):
        # Extract the nested user data from the validated data
        user_data = validated_data.pop('user')  # Use pop() to extract user data safely
        # Create a new User instance
        user = User.objects.create(**user_data)  # Create the user
        # Create the ServiceProvider instance with the created user
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
            user = instance.user  # Get the associated User object
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()  # Save User changes

        # Save the ServiceProvider instance with updated data
        instance.save()
        return instance

#     # def update(self, instance, validated_data):
#     #     user_data = validated_data.pop('user', None)  # Extract user data
#     #     # Update the user
#     #     for attr, value in user_data.items():
#     #         setattr(instance.user, attr, value)
#     #     instance.user.save()  # Save the user instance
#     #     # Update the service provider instance
#     #     for attr, value in validated_data.items():
#     #         setattr(instance, attr, value)
#     #     instance.save()  # Save the service provider instance
#     #     return instance
