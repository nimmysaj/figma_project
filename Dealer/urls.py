from django.urls import path,include
from Dealer import views
from rest_framework.routers import DefaultRouter
from Dealer.views import ServiceProviderViewSet

router = DefaultRouter() 
router.register(r'service-providers', ServiceProviderViewSet, basename='service-provider')

urlpatterns = [
    path('login/',views.DealerLoginView.as_view(),name='dealer_login'),
    path('api/', include(router.urls)),
]