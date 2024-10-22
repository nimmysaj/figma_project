from django.urls import include, path
from .views import  PaymentListView,ServiceProviderReviews,FinancialOverviewView


urlpatterns = [
   
    path('transactions/', PaymentListView.as_view(), name='payment-list'),
    path('financial/', FinancialOverviewView.as_view(), name='financial-overview'),
    path('reviews/<int:id>/', ServiceProviderReviews.as_view(), name='service-provider-reviews'),
]
