from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    # def authenticate(self, request, username=None, password=None, **kwargs):
    #     print(f"Attempting authentication for {username}")
    #     try:
    #         # Check if username is an email
    #         if '@' in username:
    #             user = User.objects.get(email=username)
    #         else:
    #             user = User.objects.get(phone_number=username)
    #     except User.DoesNotExist:
    #         print(f"No user found with {username}")
    #         return None
        
    #     if user and user.check_password(password):
    #         print(f"User {username} authenticated successfully")
    #         return user
    #     print(f"Password incorrect for {username}")
    #     print(user.password)
    #     return None

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username:
            print("No username provided")
            return None
        
        print(f"Attempting authentication for {username}")
        try:
            # Check if username is an email
            if '@' in username:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(phone_number=username)
        except User.DoesNotExist:
            print(f"No user found with {username}")
            return None
        
        if user and user.check_password(password):
            print(f"User {username} authenticated successfully")
            return user
        print(f"Password incorrect for {username}")
        return None



from social_core.backends.google import GoogleOAuth2
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

class CustomGoogleOAuth2(GoogleOAuth2):
    def get_user_details(self, response):
        """Return user details from the Google response."""
        details = super().get_user_details(response)
        
        # Ensure 'username' is not required and use email as a unique identifier
        details['username'] = response.get('email')  # Use email as username
        return details

class CustomBackend(BaseBackend):
    def authenticate(self, request, *args, **kwargs):
        """Override the authenticate method to avoid username requirement"""
        user = None
        email = kwargs.get('email')
        
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create(email=email, username=email)  # Handle this as per your custom logic
        return user
