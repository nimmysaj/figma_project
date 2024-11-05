from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


# TASK 1 Franchisee Register//////////////////////////////////////////////////////////////////////////////////////////////////
router = DefaultRouter()
router.register(r'franchisees', FranchiseeViewSet, basename='franchisee')

urlpatterns = [
    path('', include(router.urls)),
    path('franchisees/confirm-payment/', FranchiseeViewSet.as_view({'post': 'confirm_payment'}), name='confirm_payment'),
    path('generate_signature/',PaymentTestView.as_view(),name='generate_signature'),

# TASK 2 Transacion History ////////////////////////////////////////////////////////////////////////////////////////////////////

    path('ViewTransactionHistory/', TransactionListView.as_view(), name='Transaction-history-list'),
    
    
# TASK 3 Service Types and Collars //////////////////////////////////////////////////////////////////////////////////////////////
    path('service-types/', ServiceTypeAPIView.as_view(), name='service-types-api'), #Service API CRUD
    path('Collor/', CollarAPIView.as_view(), name='collor-api'), # Collor API CRUD
    path('service-types-collars/', ServiceTypeAndCollarView.as_view(), name='service_types_and_collars'), # GET Service Type and Collor API CRUD
    
    
# TASK 4 Ad Category CRUD ///////////////////////////////////////////////////////////////////////////////////////////////////////        
    path('Ad_category/', AdCategoryAPIView.as_view(), name='Ad_category-api'),
    
    
    
    
    # path('payments/', TransactionsListView.as_view(), name='payment-list'),
    # path('payments/<int:pk>/', TransactionDetailView.as_view(), name='payment-detail'),
    # path('FranchiseeTransactionHistory/', FranchiseePaymentHistory.as_view(), name='Franchisee-Transaction-History'),
]