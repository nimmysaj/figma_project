"""from django.urls import path
from .views import CreatePaymentOrderAPIView, RazorpayWebhookAPIView, VerifyPaymentAPIView

urlpatterns = [
    path('create-payment/', CreatePaymentOrderAPIView.as_view(), name='create-payment'),
    path('razorpay-webhook/', RazorpayWebhookAPIView.as_view(), name='razorpay-webhook'),
    path('verify-payment/', VerifyPaymentAPIView.as_view(), name='verify-payment'),
]
"""
from django.urls import path
from .views import CreatePaymentOrderAPIView, VerifyPaymentAPIView, payment_view

urlpatterns = [
    path('create-payment/', CreatePaymentOrderAPIView.as_view(), name='create-payment'),
    path('verify-payment/', VerifyPaymentAPIView.as_view(), name='verify-payment'),
    path('payment/', payment_view, name='payment'),
]
