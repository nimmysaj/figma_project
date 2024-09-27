from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ForgotPasswordView, VerifyOTPView, NewPasswordView,LoginView

urlpatterns = [
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('new-password/', NewPasswordView.as_view(), name='new-password'),
    path('login/',LoginView.as_view(),name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('categories/',GetCategoriesView.as_view(),name='categories'),
    path('subcategories/',GetSubcategoryView.as_view(),name='subcategories'),
]

