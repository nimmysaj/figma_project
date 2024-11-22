from django.urls import path, include
from .views import (
    ServiceProviderRequestsView,
    CustomerServiceRequestView,
    ServiceRequestInvoiceView,
    ServiceProviderLoginView,
    # ServiceRegisterViewSet,
    BookingsView,
    ServiceDetailsView,
    DeclineServiceView,
    # OnetimeLeadView,
    DeductLeadBalanceView,
    CustomConvertTokenView,
    GoogleOAuth2CompleteView

)

# from rest_framework.routers import DefaultRouter
# router = DefaultRouter()
# router.register(r'service-registers', ServiceRegisterViewSet, basename='service-register')


urlpatterns = [
    path('login/', ServiceProviderLoginView.as_view(), name = 'login'),
    path('service_requests/', ServiceProviderRequestsView.as_view(),
         name='service-provider-requests'),
    path('details/', CustomerServiceRequestView.as_view(), name="details"),
    path('invoice/', ServiceRequestInvoiceView.as_view(), name="invoice"),

    path('bookings/', BookingsView.as_view(), name='bookings'),  # GET
    path('service_details/', ServiceDetailsView.as_view(), name="service_details"),
    path('declinerequest/', DeclineServiceView.as_view(), name="decline_request"),

    # path('onetimelead/', OnetimeLeadView.as_view(), name = "onetimelead"),
    path('deductlead/', DeductLeadBalanceView.as_view(), name="deductlead"),
    path('auth/', include('drf_social_oauth2.urls')),
    path('auth/complete/google-oauth2/', GoogleOAuth2CompleteView.as_view(), name='google_oauth2_complete'),

    path('auth/convert-token/', CustomConvertTokenView.as_view(), name='convert_token'),

    # path('', include(router.urls)),
 


]
