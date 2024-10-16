from django.urls import path
from .views import ServiceRequestDetailView
from .views import UserDetailsView,UserPaymentHistoryView

urlpatterns = [
    path('service-request-detail/', ServiceRequestDetailView.as_view(), name='service-request-detail'),
    path('user-details/', UserDetailsView.as_view(), name='user-details'),
    path('user-payment-history-service/', UserPaymentHistoryView.as_view(), name='user-payment-history-service'),
]