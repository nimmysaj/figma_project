from django.urls import include, path
from service_provider.views import ResetPasswordView
from rest_framework.routers import DefaultRouter
from .views import *
from . import views



urlpatterns = [

    path('login/', DealerLoginView.as_view(), name='dealer_login'),
    path('service-providers/', DealerServiceProviderListView.as_view(), name='dealer-service-providers'),
    # path('search/', SearchAPIView.as_view(), name='search'),
    path('service-provider-counts/', DealerServiceProviderCountsView.as_view(), name='service-provider-counts'),
    path('pending-service-providers/', DealerServiceProviderPendingListView.as_view(), name='dealer-service-provider-list'),
    path('serviceproviders/<int:id>/approve/', UpdateServiceProviderStatusView.as_view(), name='approve-serviceprovider'),
    path('service-provider-details/<int:service_provider_id>/', DealerServiceProviderDetailView.as_view(), name='dealer-service-provider-detail'),

    path('payment-request/create/', PaymentRequestCreateView.as_view(), name='payment-request-create'),




    path('franchisee-details/', DealerFranchiseeDetailView.as_view(), name='dealer-franchisee-details'),
    path('api/franchise/details/', franchise_details_view, name='franchise-details'),



]