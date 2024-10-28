from django.urls import include, path
from .views import ServiceProviderView,ProviderSearchView,DealerLoginView

urlpatterns = [
    path('login/', DealerLoginView.as_view(), name='dealer_login'),
    path('service-providers-details/', ServiceProviderView.as_view(), name='service-provider-details'),
    path('service-providers-search/', ProviderSearchView.as_view(), name='service-provider-search'),
]