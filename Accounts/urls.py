from django.urls import path
from Accounts.views import ServiceProviderLoginView, ServiceProviderPasswordResetView, ResetPasswordView

urlpatterns = [
    path('login/', ServiceProviderLoginView.as_view(), name='service-provider-login'),
    path('service-provider/password-reset/', ServiceProviderPasswordResetView.as_view(), name='service-provider-password-reset'),
    path('service-provider/password-reset/<uidb64>/<token>/', ResetPasswordView.as_view(), name='service-provider-password-reset-confirm'),
]
