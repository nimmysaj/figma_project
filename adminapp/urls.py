from django.urls import path
from .views import ServiceRequestDetailView

urlpatterns = [
    path('service-request-detail/', ServiceRequestDetailView.as_view(), name='service-request-detail'),
]