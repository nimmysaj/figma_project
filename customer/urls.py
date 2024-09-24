from django.urls import path
from .views import CustomerProfileCreateView, CustomerProfileDetailView

urlpatterns = [
    path('profile/create/', CustomerProfileCreateView.as_view(), name='profile-create'),
    path('profile/<int:pk>/', CustomerProfileDetailView.as_view(), name='profile-detail'),
]
