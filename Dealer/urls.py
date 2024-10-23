from django.urls import path
from .views import DealerFranchiseeListView, DealerPaymentHistoryView

urlpatterns = [
    path('dealer/franchisee/', DealerFranchiseeListView.as_view(), name='dealer-franchisee-list'),
    path('dealer/payment-history/', DealerPaymentHistoryView.as_view(), name='dealer-payment-history'),
]
