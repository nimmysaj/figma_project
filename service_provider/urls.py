from django.urls import path
from .views import ServiceProviderLoginView, ServiceProviderPasswordForgotView, ServiceProviderPasswordForgotView, ResetPasswordView, ServiceProviderViewSet, SetNewPasswordView

urlpatterns = [
    path('login/', ServiceProviderLoginView.as_view(), name='service-provider-login'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    #forgot password
    path('password-forgot/', ServiceProviderPasswordForgotView.as_view(), name='service-provider-password-forgot'),
    path('password-reset/<uidb64>/<token>/', ResetPasswordView.as_view(), name='service-provider-password-reset-confirm'),
    #profile update
    path('profile/<int:pk>/', ServiceProviderViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update',
        'patch': 'partial_update'
        }), name='profile_update')
]
