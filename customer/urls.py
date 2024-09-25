from django.urls import path
from .views import CustomerProfileCreateView, CustomerProfileListView, CustomerProfileDetailView

urlpatterns = [
    path('profile/create/', CustomerProfileCreateView.as_view(), name='customer-create'),
    path('profile/list/', CustomerProfileListView.as_view(), name='customer-list'),
    path('profile/<int:pk>/', CustomerProfileDetailView.as_view(), name='customer-detail'),
]



