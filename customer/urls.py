from django.urls import include, path
# from service_provider.views import ResetPasswordView
from .views import CategoryListView, CustomerLoginView, CustomerPasswordForgotView, CustomerViewSet, RegisterView, ServiceProviderDetailView, ServiceProviderListView, ServiceRequestCreateView, ServiceRequestDetailView, ServiceRequestInvoiceDetailView, SubcategoryListView, UnifiedSearchView, VerifyOTPView
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register_customer'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    #login
    path('login/', CustomerLoginView.as_view(), name='customer-login'),
    #forgot password
    path('password-forgot/', CustomerPasswordForgotView.as_view(), name='customer-password-forgot'),
    # path('password-reset/<uidb64>/<token>/', ResetPasswordView.as_view(), name='customer-password-reset-confirm'),
    #profile update
    path('profile/<int:pk>/', CustomerViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update',
        'patch': 'partial_update'
        }), name='profile_update'),
    #category, subcategory, service_providers_list, detailed view of service providers
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:category_id>/subcategories/', SubcategoryListView.as_view(), name='subcategory-list'),
    path('subcategories/<int:subcategory_id>/service-providers/', ServiceProviderListView.as_view(), name='serviceprovider-list'),
    path('service_provider/<int:id>/', ServiceProviderDetailView.as_view(), name='service_provider_detail'),
    #search_functionality
    path('search/', UnifiedSearchView.as_view(), name='unified-search'),
    #service request upto booking details
    path('service-request/', ServiceRequestCreateView.as_view(), name='service-request-create'),
    path('view-request-user/', ServiceRequestDetailView.as_view(), name='view-request-user'),
    path('service-request-invoice/', ServiceRequestInvoiceDetailView.as_view(), name='service-request-invoice-detail'),
]
