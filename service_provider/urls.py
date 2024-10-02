from django.urls import path
from .views import (
    ServiceRegisterViewSet,
    ComplaintViewSet
)

urlpatterns = [
    path('service-registers/', ServiceRegisterViewSet.as_view({'get': 'list', 'post': 'create'}), name='service-register-list'),
    path('service-registers/<int:pk>/', ServiceRegisterViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='service-register-detail'),
    path('complaints/<int:pk>/update_status/', ComplaintViewSet.as_view({'post': 'update_status'}), name='complaint-update-status'),

]