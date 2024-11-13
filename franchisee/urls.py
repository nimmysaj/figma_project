# urls.py
from django.urls import path
from .views import FranchiseeRegistrationView,FranchiseeLoginView,CustomTokenObtainPairView,CustomTokenRefreshView,ServiceProviderCreateAPIView,DealerCreateView,DealerListView


urlpatterns = [
    path('franchiseeregister/', FranchiseeRegistrationView.as_view(), name='franchisee-register'),
    path('franchiseelogin/',FranchiseeLoginView.as_view(),name='franchisee_login'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('addserviceprovider/',ServiceProviderCreateAPIView.as_view(),name='add-service-provider'),
    path('Adddealers/',DealerCreateView.as_view(),name = 'dealers_Add'),
    path('dealers/', DealerListView.as_view(), name='dealer-list'),

]
