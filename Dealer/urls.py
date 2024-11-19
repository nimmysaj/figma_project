from django.urls import include, path
from .views import ServiceProviderListView,ProviderSearchView,LoginView,ProviderSortView
from django.urls import path, include,include
from rest_framework.routers import DefaultRouter
from .views import ServiceProviderViewSet

router = DefaultRouter()
router.register(r'service-providers', ServiceProviderViewSet)
from rest_framework.routers import DefaultRouter
from Dealer.views import ServiceProviderViewSet

router = DefaultRouter() 
router.register(r'service-providers', ServiceProviderViewSet, basename='service-provider')
from django.urls import path
from .views import ServiceProviderVerificationListCreate, ServiceProviderVerificationDetail,LoginView, DealerFranchiseeListView, DealerPaymentHistoryView
from Dealer import views

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('service-providers-details/', ServiceProviderListView.as_view(), name='service-provider-details'),
    path('service-providers-search/', ProviderSearchView.as_view(), name='service-provider-search'),
    path('service-providers-sort/', ProviderSortView.as_view(), name='service-provider-sort'),
    path('api/', include(router.urls)),
    path('service-providers/', ServiceProviderVerificationListCreate.as_view(), name='service-providers-list'),
    path('service-providers/<int:pk>/', ServiceProviderVerificationDetail.as_view(), name='service-provider-detail'),
    path('serviceprovider/verification/',views.ServiceProviderVerificationListView.as_view()),
    path('dealer/franchisee/', DealerFranchiseeListView.as_view(), name='dealer-franchisee-list'),
    path('dealer/payment-history/', DealerPaymentHistoryView.as_view(), name='dealer-payment-history'),
]