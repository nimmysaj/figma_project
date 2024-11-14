from django.urls import path,include
from franchise import views
from rest_framework.routers import DefaultRouter
from franchise.views import FranchiseServiceProviderViewSet

router = DefaultRouter() 
router.register(r'service-providers', FranchiseServiceProviderViewSet, basename='service-provider')

urlpatterns = [
    path('dealer/<int:pk>/',views.DealerDetailView.as_view(),name='dealer-details'),
    path('dealer/search/',views.DealerSearchView.as_view(),name='dealer-search'),
    path('login/',views.FranchiseeLoginView.as_view(),name='franchisee-login'),
    path('sp/', include(router.urls)),
]