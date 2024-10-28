from django.urls import path
from .views import ServiceProviderVerificationListCreate, ServiceProviderVerificationDetail,DealerLoginView, DealerFranchiseeListView, DealerPaymentHistoryView
from Dealer import views

urlpatterns = [
    path('service-providers/', ServiceProviderVerificationListCreate.as_view(), name='service-providers-list'),
    path('service-providers/<int:pk>/', ServiceProviderVerificationDetail.as_view(), name='service-provider-detail'),
    path('login/', DealerLoginView.as_view(), name='dealer_login'),
    path('serviceprovider/verification/',views.ServiceProviderVerificationListView.as_view()),
    path('dealer/franchisee/', DealerFranchiseeListView.as_view(), name='dealer-franchisee-list'),
    path('dealer/payment-history/', DealerPaymentHistoryView.as_view(), name='dealer-payment-history'),
]



