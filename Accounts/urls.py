from django.urls import path
from .views import InvoiceCreateView, PaymentView, VerifyPaymentView, payment_page

urlpatterns = [
    path('invoices/', InvoiceCreateView.as_view(), name='create-invoice'),
    path('invoices/payment/', PaymentView.as_view(), name='make-payment'),
    path('payment/verify/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('payment/<int:invoice_id>/', payment_page, name='payment-page'),
]
