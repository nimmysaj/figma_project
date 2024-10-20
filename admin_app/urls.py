from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FranchiseeViewSet
from .views import *
# from .views import FranchiseePaymentHistory,TransactionsListView, TransactionDetailView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'franchisees', FranchiseeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('ViewTransactionHistory/', TransactionListView.as_view(), name='Transaction-history-list'),
    # path('payments/', TransactionsListView.as_view(), name='payment-list'),
    # path('payments/<int:pk>/', TransactionDetailView.as_view(), name='payment-detail'),
    # path('FranchiseeTransactionHistory/', FranchiseePaymentHistory.as_view(), name='Franchisee-Transaction-History'),
]