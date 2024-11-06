from django.urls import path
from .views import  ServiceRequestCreateView, ServiceRequestDetailView, ServiceRequestInvoiceDetailView, ActiveServicesView  # LoginView, RegisterView, VerifyOTPView,
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    #path('login/', LoginView.as_view(), name='login'),
    #path('register/', RegisterView.as_view(), name='register'),
    #path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('service-request/', ServiceRequestCreateView.as_view(), name='service-request-create'),
    path('view-request-user/', ServiceRequestDetailView.as_view(), name='view-request-user'),
    path('service-request-invoice/', ServiceRequestInvoiceDetailView.as_view(), name='service-request-invoice-detail'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('active-services/', ActiveServicesView.as_view(), name='active-services'),

]
