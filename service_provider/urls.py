from django.urls import path
from .views import RegisterView, OTPVerificationView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify_otp'),
]
