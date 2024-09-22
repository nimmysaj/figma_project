from django.urls import path
from .views import ServiceProviderLoginView, ServiceProviderPasswordResetView, ResetPasswordView  

urlpatterns = [
    path('service-provider/login/', ServiceProviderLoginView.as_view(), name='service_provider_login'),
    path('service-provider/password-reset/', ServiceProviderPasswordResetView.as_view(), name='service_provider_password_reset'),  
    path('service-provider/password-reset/<uidb64>/<token>/', ResetPasswordView.as_view(), name="password-reset-confirm"),
]
