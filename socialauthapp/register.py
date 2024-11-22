from django.contrib.auth import authenticate
from Accounts.models import User
import os
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


def register_social_user(provider, user_id, email, name):
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():
        if provider == filtered_user_by_email[0].auth_provider:
            registered_user = authenticate(
                email=email, password=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
            )
            return {
                'email': registered_user.email,
                'tokens': registered_user.tokens()
            }
        else:
            raise AuthenticationFailed(
                detail=f'Please continue your login using {filtered_user_by_email[0].auth_provider}'
            )
    else:
        user = {
            'email': email,
            'password': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
        }
        user = User.objects.create_user(**user)
        user.is_verified = True
        user.auth_provider = provider
        user.save()

        new_user = authenticate(
            email=email, password=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
        )
        return {
            'email': new_user.email,
            'tokens': new_user.tokens()
        }
