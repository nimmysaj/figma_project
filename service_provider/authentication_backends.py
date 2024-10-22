from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
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
        print(user.password)
        return None