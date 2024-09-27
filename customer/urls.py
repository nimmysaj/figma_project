from django.urls import path
from .views import UserRegistrationView,OTPVerificationView#UserProfileView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('verifyotp/', OTPVerificationView.as_view(), name='verifyotp'),
    # path('user/profile/', UserProfileView.as_view(), name='user-profile'),
]