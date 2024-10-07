from django.urls import path
from service_provider.views import ServiceProviderViewSet, InitiatePaymentView, ConfirmPaymentView

urlpatterns = [
path('initiate-payment/', InitiatePaymentView.as_view(), name='initiate-payment'),
path('confirm-payment/', ConfirmPaymentView.as_view(), name='confirm-payment'),
    
        




















    path('serviceprovider/',ServiceProviderViewSet.as_view({
        'get':'list',
        'post':'create'
        }),name ='service'),

    path('serviceproviders/<int:pk>/', ServiceProviderViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update',
        'patch': 'partial_update'
        }), name='service_update'),


]