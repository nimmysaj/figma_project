from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FranchiseeViewSet
from .views import FranchiseePaymentHistory

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'franchisees', FranchiseeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('FranchiseeTransactionHistory/', FranchiseePaymentHistory.as_view(), name='Franchisee-Transaction-History'),
]