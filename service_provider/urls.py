from django.urls import path
from .views import ServiceProviderRegistrationView, OTPVerificationView

urlpatterns = [
    path('register/', ServiceProviderRegistrationView.as_view(), name='register'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify-otp'),
]
