# urls.py
from django.urls import path
from .views import FranchiseeRegistrationView,FranchiseeLoginView,CustomTokenObtainPairView,CustomTokenRefreshView,ServiceProviderCreateAPIView


urlpatterns = [
    path('franchiseeregister/', FranchiseeRegistrationView.as_view(), name='franchisee-register'),
    path('franchiseelogin/',FranchiseeLoginView.as_view(),name='franchisee_login'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('addserviceprovider/',ServiceProviderCreateAPIView.as_view(),name='add-service-provider'),
]
