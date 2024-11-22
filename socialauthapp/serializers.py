from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from . import google
from .register import register_social_user
from django.conf import settings


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        # Get the user data (either user info or an error message)
        user_data = google.Google.validate(auth_token)

        # If the response is an error, raise a validation error
        if "error" in user_data:
            raise serializers.ValidationError(user_data["error"])

        # Now that we know the token is valid, proceed with the user info
        if user_data['aud'] != settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY:
            raise AuthenticationFailed('Token audience does not match SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')

        user_id = user_data['sub']
        email = user_data['email']
        name = user_data['name']
        provider = 'google'

        return register_social_user(
            provider=provider, user_id=user_id, email=email, name=name
        )
