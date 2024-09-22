from django.urls import path
from service_provider.views import ServiceProviderViewSet

urlpatterns = [
    path('service/', ServiceProviderViewSet.as_view({'get':'list','post':'create'}),name='service')
]