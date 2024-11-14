from django.urls import include, path
from .views import  ServiceProviderLoginView,PaymentListView,FinancialOverviewView,BoostServiceCreateView


urlpatterns = [
    path('login/', ServiceProviderLoginView.as_view(), name='service-provider-login'),
    path('transactions/', PaymentListView.as_view(), name='payment-list'),
    path('financial/', FinancialOverviewView.as_view(), name='financial-overview'),
    # path('boost-service/', BoostServiceView.as_view(), name='boost-service'),
    path('boost-service/', BoostServiceCreateView.as_view(), name='boost-service-create'),

]
