from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FranchiseeViewSet
from .views import TransactionsListView, TransactionDetailView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'franchisees', FranchiseeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('payments/', TransactionsListView.as_view(), name='payment-list'),
    path('payments/<int:pk>/', TransactionDetailView.as_view(), name='payment-detail')
]