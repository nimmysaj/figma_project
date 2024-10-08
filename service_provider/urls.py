from django.urls import path
from .views import (
   
    ServiceRegisterViewSet,
    ComplaintViewSet,
)

urlpatterns = [
    path('service-registers/', ServiceRegisterViewSet.as_view({'get': 'list', 'post': 'create'}), name='service-register-list'),
    path('service-registers/<uuid:pk>/add-lead-balance/', ServiceRegisterViewSet.as_view({'patch': 'add_lead_balance'}), name='add-lead-balance'),
    path('service-registers/<uuid:pk>/', ServiceRegisterViewSet.as_view({'get': 'retrieve', 'patch': 'update', 'delete': 'destroy'}), name='service-register-detail'),
    path('complaints/<int:pk>/update_status/', ComplaintViewSet.as_view({'post': 'update_status'}), name='complaint-update-status'),

]