from django.urls import path
from .views import CustomerServiceRequestsView

urlpatterns = [
    path('customer/<int:servicerequest_id>/service-requests/', CustomerServiceRequestsView.as_view(), name='customer-service-requests'),
]