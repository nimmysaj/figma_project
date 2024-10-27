from django.urls import include, path
from .views import FranchiseServiceProviderDetailView, FranchiseeLoginView, FranchiseePasswordForgotView, ResetPasswordView,  FranchiseeViewSet, FranchiseeRegisterViewSet, SetNewPasswordView,FranchiseeRegister,Franchisee,AddServiceProviderView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'franchisee-registers', FranchiseeRegisterViewSet, basename='service-register')

urlpatterns=[
    path('login/', FranchiseeLoginView.as_view(), name='franchisee-login'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    #forgot password
    path('password-forgot/', FranchiseePasswordForgotView.as_view(), name='franchisee-password-forgot'),
    path('password-reset/<uidb64>/<token>/', ResetPasswordView.as_view(), name='franchisee-password-reset-confirm'),
    #profile update
    path('profile/<int:pk>/', FranchiseeViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update',
        'patch': 'partial_update'
        }), name='profile_update'),
    path('service-provider/', FranchiseServiceProviderDetailView.as_view(), name='franchise-service-provider-detail'),
]
