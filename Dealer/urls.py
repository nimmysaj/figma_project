from django.urls import include, path
from .views import ServiceProviderListView,ProviderSearchView,LoginView,ProviderSortView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceProviderViewSet

router = DefaultRouter()
router.register(r'service-providers', ServiceProviderViewSet)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('service-providers-details/', ServiceProviderListView.as_view(), name='service-provider-details'),
    path('service-providers-search/', ProviderSearchView.as_view(), name='service-provider-search'),
    path('service-providers-sort/', ProviderSortView.as_view(), name='service-provider-sort'),
]
