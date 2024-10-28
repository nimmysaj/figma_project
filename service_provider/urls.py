from django.urls import include, path
from .views import ServiceProviderLoginView, FranchiseListView

urlpatterns = [
    path('login/', ServiceProviderLoginView.as_view(), name='service-provider-login'),
    path('franchisee/', FranchiseListView.as_view(), name='franchisee-list'),
]

