<<<<<<< HEAD
from django.urls import path
from .views import ServiceProviderVerificationListCreate, ServiceProviderVerificationDetail,DealerLoginView

urlpatterns = [
    path('service-providers/', ServiceProviderVerificationListCreate.as_view(), name='service-providers-list'),
    path('service-providers/<int:pk>/', ServiceProviderVerificationDetail.as_view(), name='service-provider-detail'),
    path('login/', DealerLoginView.as_view(), name='dealer_login'),

=======
from django.urls import include, path
from .views import ServiceProviderView,ProviderSearchView,DealerLoginView

urlpatterns = [
    path('login/', DealerLoginView.as_view(), name='dealer_login'),
    path('service-providers-details/', ServiceProviderView.as_view(), name='service-provider-details'),
    path('service-providers-search/', ProviderSearchView.as_view(), name='service-provider-search'),
>>>>>>> f568851c93265555359d959eef8979965dcd140b
]