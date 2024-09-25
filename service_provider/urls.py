

from django.urls import path
from service_provider.views import ServiceProviderViewSet

urlpatterns = [

    path('service/', ServiceProviderViewSet.as_view({
        'post': 'create',
    }), name='service-create'),
   
    path('serviceprovider/<int:pk>/', ServiceProviderViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        }), name='service'),
]  