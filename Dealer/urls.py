from django.urls import path
from .views import DealerPaymentRequestAPIView

urlpatterns = [
    path('api/dealer/payment-request/', DealerPaymentRequestAPIView.as_view(), name='dealer-payment-request'),
]
