from django.urls import include, path
from .views import ServiceProviderView,ProviderSearchView,LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('service-providers-details/', ServiceProviderView.as_view(), name='service-provider-details'),
    path('service-providers-search/', ProviderSearchView.as_view(), name='service-provider-search'),
]