# accounts/urls.py

from django.urls import path
from .views import ForgotPasswordView, VerifyOTPView, NewPasswordView

urlpatterns = [
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('new-password/', NewPasswordView.as_view(), name='new-password'),
]

