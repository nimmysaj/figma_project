from django.urls import path
from service_provider.views import ServiceProviderViewSet

urlpatterns = [
    path('serviceprovider/',ServiceProviderViewSet.as_view({
        'get':'list',
        'post':'create'
        }),name ='service'),

    path('serviceproviders/<int:pk>/', ServiceProviderViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update',
        'patch': 'partial_update'
        }), name='service_update')
        
]