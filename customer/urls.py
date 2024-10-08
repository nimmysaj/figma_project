from django.urls import path
from .views import ServiceRequestListView, ServiceRequestDetailView
from service_provider.views import ResetPasswordView
<<<<<<< HEAD
from .views import CustomerLoginView, CustomerPasswordForgotView, CustomerViewSet, RegisterView, VerifyOTPView
# from .views import #CustomerActiveServicesList
=======
from .views import CustomerLoginView, CustomerPasswordForgotView, CustomerViewSet, RegisterView, VerifyOTPView, CustomerActiveServicesList

>>>>>>> 7bc5d32ad28ed6ffaba33c62da259b94ff5d4ba3
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
<<<<<<< HEAD
    path('service-requests/', ServiceRequestListView.as_view(), name='service-requests-list'),
    path('service-requests/<int:id>/', ServiceRequestDetailView.as_view(), name='service-request-detail')

=======
    path('customers/<int:customer_id>/active-services/', CustomerActiveServicesList.as_view(), name='customer-active-services'),
>>>>>>> 7bc5d32ad28ed6ffaba33c62da259b94ff5d4ba3
]
