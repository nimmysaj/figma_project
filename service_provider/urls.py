from django.urls import include, path
from .views import  ServiceProviderLoginView,PaymentListView,FinancialOverviewView


urlpatterns = [
    path('login/', ServiceProviderLoginView.as_view(), name='service-provider-login'),
    path('transactions/', PaymentListView.as_view(), name='payment-list'),
    path('financial/', FinancialOverviewView.as_view(), name='financial-overview'),

]
