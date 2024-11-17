from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


# Franchisee Register//////////////////////////////////////////////////////////////////////////////////////////////////


urlpatterns = [
    path('franchisee/', FranchiseeView.as_view(), name='franchisee'),

# Transacion History ////////////////////////////////////////////////////////////////////////////////////////////////////

    path('ViewTransactionHistory/', TransactionListView.as_view(), name='Transaction-history-list'),
    
# Service Types and Collars //////////////////////////////////////////////////////////////////////////////////////////////
    path('service-types/', ServiceTypeAPIView.as_view(), name='service-types-api'), #Service API CRUD
    path('Collor/', CollarAPIView.as_view(), name='collor-api'), # Collor API CRUD
    path('service-types-collars/', ServiceTypeAndCollarView.as_view(), name='service_types_and_collars'), # GET Service Type and Collor API CRUD
    
# Ad Category CRUD ///////////////////////////////////////////////////////////////////////////////////////////////////////        
    path('Ad_category/', AdCategoryAPIView.as_view(), name='Ad_category-api'),
    
# ADD Expenses
    path('Add_expenses/', AddExpenseView.as_view(), name='Add_expenses_api'),

]