from django.urls import path

from service_provider.views import ResetPasswordView
from .views import CustomerLoginView, CustomerPasswordForgotView, CustomerViewSet, RegisterView, VerifyOTPView,NearbyServiceProviders

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register_customer'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    #login
    path('login/', CustomerLoginView.as_view(), name='customer-login'),
    #forgot password
    path('password-forgot/', CustomerPasswordForgotView.as_view(), name='customer-password-forgot'),
    path('password-reset/<uidb64>/<token>/', ResetPasswordView.as_view(), name='customer-password-reset-confirm'),
    #profile update
    path('profile/<int:pk>/', CustomerViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update',
        'patch': 'partial_update'
        }), name='profile_update'),

    path('service-providers/nearby/',NearbyServiceProviders.as_view(), name='nearby_service_providers'),
]