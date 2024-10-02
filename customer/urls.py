from django.urls import path
from .views import (
    CustomerProfileCreateView, 
    CustomerProfileDetailView, 
    CustomerProfileListView, 
)

urlpatterns = [
    # Customer profile endpoints
    path('create/', CustomerProfileCreateView.as_view(), name='create_customer_profile'),
    path('<int:pk>/edit/', CustomerProfileDetailView.as_view(), name='edit_customer_profile'),
    path('<int:pk>/', CustomerProfileListView.as_view(), name='view_customer_profile'),
]



