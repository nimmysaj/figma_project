from django.urls import path,include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ForgotPasswordView, VerifyOTPView, NewPasswordView,LoginView,CategoryViewSet,SubcategoryViewSet,SubcategoryServiceProviders,ResendOTP

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'subcategories', SubcategoryViewSet, basename='subcategory')

urlpatterns = [
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('resend-otp/', ResendOTP.as_view(), name='resend-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('new-password/', NewPasswordView.as_view(), name='new-password'),
    path('login/', LoginView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Service provider URL
    path('subcategories/<int:subcategory_id>/service_providers/', SubcategoryServiceProviders.as_view(), name='subcategory_service_providers'),
    path('', include(router.urls))
   
]





