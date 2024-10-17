from django.urls import path
from .views import AddFranchiseType,ServiceHistoryView,FranchiseeDetailsView

urlpatterns = [
    path('franchise-register/', AddFranchiseType.as_view(), name='franchise-register'),
    path('service-history/',ServiceHistoryView.as_view(),name='service-history'),
    path('franchisee-details/',FranchiseeDetailsView.as_view(),name='franchisee-details'),
]