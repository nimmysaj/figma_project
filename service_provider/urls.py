from django.urls import include, path
from .views import CustomerServiceRequestView, ServiceProviderLoginView, ServiceProviderPasswordForgotView, ServiceProviderPasswordForgotView, ResetPasswordView, ServiceProviderRequestsView, ServiceProviderViewSet, ServiceRegisterViewSet, ServiceRequestInvoiceView, SetNewPasswordView, CompletedWorkListView, OngoingWorkListView, ServiceRequestStatusCheckView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'service-registers', ServiceRegisterViewSet, basename='service-register')


urlpatterns = [
    path('login/', ServiceProviderLoginView.as_view(), name='service-provider-login'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    #forgot password
    path('password-forgot/', ServiceProviderPasswordForgotView.as_view(), name='service-provider-password-forgot'),
    path('password-reset/<uidb64>/<token>/', ResetPasswordView.as_view(), name='service-provider-password-reset-confirm'),
    #profile update
    path('profile/<int:pk>/', ServiceProviderViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update',
        'patch': 'partial_update'
        }), name='profile_update'),
    path('', include(router.urls)),
    path('service-requests/', ServiceProviderRequestsView.as_view(), name='service-provider-requests'),
    path('service-requests/details/<int:pk>/', CustomerServiceRequestView.as_view(), name="details"),
    path('invoice/<int:pk>/', ServiceRequestInvoiceView.as_view(), name="invoice"),
    path('completed-work/', CompletedWorkListView.as_view(), name='completed-work'),
    path('ongoing-work/', OngoingWorkListView.as_view(), name='ongoing-work'),
    path('change-work-status/', ServiceRequestStatusCheckView.as_view(), name='check-work-status'),
]
