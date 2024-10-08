from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, PaymentInitiationView, PaymentConfirmationView, razorpay_payment_page

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('initiate-payment/', PaymentInitiationView.as_view(), name='initiate-payment'),
    path('confirm-payment/', PaymentConfirmationView.as_view(), name='confirm-payment'),
    path('pay-invoice/<int:invoice_id>/', razorpay_payment_page, name='razorpay-payment'),
    ]
