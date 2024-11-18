from django.urls import path,include
from franchise import views
from rest_framework.routers import DefaultRouter
from franchise.views import FranchiseServiceProviderViewSet

router = DefaultRouter() 
router.register(r'service-providers', FranchiseServiceProviderViewSet, basename='service-provider')

urlpatterns = [
    path('login/',views.FranchiseeLoginView.as_view(),name='franchisee-login'),
    path('sp/', include(router.urls)),
    path('dealer-detail/',views.DealerdetailView.as_view())
]