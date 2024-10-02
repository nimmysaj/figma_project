from django.urls import path
from .views import (
    ServiceProviderRequestsView, 
    CustomerServiceRequestView,
    ServiceRequestInvoiceView
    )

urlpatterns = [
    path('service_requests/', ServiceProviderRequestsView.as_view(), name='service-provider-requests'),
    path('details/<int:pk>/', CustomerServiceRequestView.as_view(), name="details"),
    path('invoice/<int:pk>/', ServiceRequestInvoiceView.as_view(), name="invoice")
]
