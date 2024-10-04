from django.urls import path
from .views import  ServiceRequestCreateView, ServiceRequestDetailView, ServiceRequestInvoiceDetailView  # LoginView, RegisterView, VerifyOTPView,

urlpatterns = [
    #path('login/', LoginView.as_view(), name='login'),
    #path('register/', RegisterView.as_view(), name='register'),
    #path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('service-request/', ServiceRequestCreateView.as_view(), name='service-request-create'),
    path('view-request-user/', ServiceRequestDetailView.as_view(), name='view-request-user'),
    path('service-request-invoice/', ServiceRequestInvoiceDetailView.as_view(), name='service-request-invoice-detail'),

]
