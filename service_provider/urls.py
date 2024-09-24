from django.urls import path
from .views import (
    ServiceRegisterViewSet
)

urlpatterns = [
    path('service-registers/', ServiceRegisterViewSet.as_view({'get': 'list', 'post': 'create'}), name='service-register-list'),
    path('service-registers/<int:pk>/', ServiceRegisterViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='service-register-detail'),
]
