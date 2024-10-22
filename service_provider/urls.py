from django.urls import path, include
from .views import (
    ServiceProviderRequestsView,
    CustomerServiceRequestView,
    ServiceRequestInvoiceView,
    # ServiceProviderLoginView,
    # ServiceRegisterViewSet,
    BookingsView,
    ServiceDetailsView,
    DeclineServiceView,
    # OnetimeLeadView,
    DeductLeadBalanceView
)

# from rest_framework.routers import DefaultRouter
# router = DefaultRouter()
# router.register(r'service-registers', ServiceRegisterViewSet, basename='service-register')


urlpatterns = [
    # path('login/', ServiceProviderLoginView.as_view(), name = 'login'),
    path('service_requests/', ServiceProviderRequestsView.as_view(),
         name='service-provider-requests'),
    path('details/', CustomerServiceRequestView.as_view(), name="details"),
    path('invoice/', ServiceRequestInvoiceView.as_view(), name="invoice"),

    path('bookings/', BookingsView.as_view(), name='bookings'),  # GET
    path('service_details/', ServiceDetailsView.as_view(), name="service_details"),
    path('declinerequest/', DeclineServiceView.as_view(), name="decline_request"),

    # path('onetimelead/', OnetimeLeadView.as_view(), name = "onetimelead"),
    path('deductlead/', DeductLeadBalanceView.as_view(), name="deductlead"),

    # path('', include(router.urls)),

]
