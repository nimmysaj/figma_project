from django.urls import path
from .views import get_service_request_by_id

urlpatterns = [
    path('api/service-request/<int:id>/', get_service_request_by_id, name='get_service_request_by_id'),
]