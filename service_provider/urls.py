from django.urls import include, path
from .views import BookingsServiceRequestsView, ComplaintViewSet, CompletedServiceRequestView, CustomerServiceRequestView, DeclineServiceView, DeductLeadBalanceView, FinancialOverviewView, OngoingServiceRequestView, PaymentListView, ServiceDetailsView, ServiceProviderLoginView, ServiceProviderPasswordForgotView, ServiceProviderPasswordForgotView, ResetPasswordView, ServiceProviderRequestsView, ServiceProviderReviews, ServiceProviderViewSet, ServiceRegisterViewSet, ServiceRequestCompleteStatus, ServiceRequestInvoiceView, SetNewPasswordView,ServiceProviderCountsView, ServiceProviderDetailsView, ServiceProviderRevenueView, ServiceReachView, UpdateLocationView, ProviderLocationDistanceView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'service-registers', ServiceRegisterViewSet, basename='service-register')
router.register(r'complaints', ComplaintViewSet, basename='complaint')


urlpatterns = [
    path('login/', ServiceProviderLoginView.as_view(), name='service-provider-login'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    #forgot password
    path('password-forgot/', ServiceProviderPasswordForgotView.as_view(), name='service-provider-password-forgot'),
    path('password-reset/<uidb64>/<token>/', ResetPasswordView.as_view(), name='service-provider-password-reset-confirm'),
    #profile update
    path('profile/', ServiceProviderViewSet.as_view({'get': 'retrieve', 'put': 'update','patch': 'partial_update'}), name='profile_update'),
    #service register,edit,lead balance
    path('', include(router.urls)),
    #service request
    path('service-requests/', ServiceProviderRequestsView.as_view(), name='service-provider-requests'),
    path('service-requests/details/<int:pk>/', CustomerServiceRequestView.as_view(), name="details"),
    path('invoice/<int:pk>/', ServiceRequestInvoiceView.as_view(), name="invoice"),
    #bookings and appointments
    path('bookings/', BookingsServiceRequestsView.as_view(), name="bookings"),
    path('service_details/<pk>/', ServiceDetailsView.as_view(), name="service_details"),
    path('declinerequest/', DeclineServiceView.as_view(), name="decline_request"),
    #deduct lead
    path('deductlead/', DeductLeadBalanceView.as_view(), name="deductlead"),
    #complaints
    #path('', include(router.urls)),
    #Active services
    path('ongoing/', OngoingServiceRequestView.as_view(), name="ongoing"),
    path('completed/', CompletedServiceRequestView.as_view(), name="completed"),
    path('change-work-status/', ServiceRequestCompleteStatus.as_view(), name='check-work-status'),
    #transactions
    path('transactions/', PaymentListView.as_view(), name='payment-list'),
    path('financial/', FinancialOverviewView.as_view(), name='financial-overview'),
    path('reviews/', ServiceProviderReviews.as_view(), name='service-provider-reviews'),
    
    #dashboard
    path('counts/', ServiceProviderCountsView.as_view(), name='service-provider-counts'),
    path('details-view/', ServiceProviderDetailsView.as_view(), name='service-provider-details') ,
    path('revenue/', ServiceProviderRevenueView.as_view(), name="service-provider-revenue"),
    path('service-reach/', ServiceReachView.as_view(), name="service-reach"),

    #location
    path('update-location/', UpdateLocationView.as_view(), name="providers-location"),
    path('location-distance/', ProviderLocationDistanceView.as_view(), name="providers-location-distance"),
    
]