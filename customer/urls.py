from django.urls import path
from .views import OngoingServiceRequestListView, CompletedServiceRequestListView, ServiceRequestDetailView
from service_provider.views import ResetPasswordView
from .views import CustomerLoginView, CustomerPasswordForgotView, CustomerViewSet, RegisterView, VerifyOTPView
# from .views import #CustomerActiveServicesList
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
    path('service-requests/ongoing/', OngoingServiceRequestListView.as_view(), name='ongoing-service-requests'),
    path('service-requests/completed/', CompletedServiceRequestListView.as_view(), name='completed-service-requests'),
    path('service-requests/<int:id>/', ServiceRequestDetailView.as_view(), name='service-request-detail')

]
