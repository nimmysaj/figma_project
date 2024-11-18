from django.urls import include, path
from .views import ServiceProviderListView,ProviderSearchView,LoginView,ProviderSortView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('service-providers-details/', ServiceProviderListView.as_view(), name='service-provider-details'),
    path('service-providers-search/', ProviderSearchView.as_view(), name='service-provider-search'),
    path('service-providers-sort/', ProviderSortView.as_view(), name='service-provider-sort'),
]
