from django.urls import path
from .views import FranchiseeLoginView, FranchiseeListView, FranchisePaymentHistoryView, FranchiseeComplaintsListAPIView, IncompleteBookingsListAPIView


urlpatterns = [
    path('login/', FranchiseeLoginView.as_view(), name='franchise_login'),
    path('franchiseedetails/', FranchiseeListView.as_view(), name='franchisee-list'),
    path('payment-history/', FranchisePaymentHistoryView.as_view(), name='franchisee-payment-history'),
    path('complaints/', FranchiseeComplaintsListAPIView.as_view(), name='api-franchisee-complaints'),
    path('incomplete-bookings/', IncompleteBookingsListAPIView.as_view(), name='api-incomplete-bookings'),

]
