from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import *
from . import views



urlpatterns = [
    path('login/', FranchiseeLoginView.as_view(), name='franchise-login'),
    path('service-providers/', FranchiseeServiceProviderListView.as_view(), name='franchise-service-providers'),
    # path('service-providers/<str:sort_option>/', FranchiseeServiceProviderListView.as_view(), name='franchise-service-providers'),
    path('service-provider-counts/', FranchiseeServiceProviderCountsView.as_view(), name='franchisee-service-provider-counts'),
    path('service-provider-details/<int:service_provider_id>/', FranchiseeServiceProviderDetailView.as_view(), name='franchisee-service-provider-detail'),

    path('franchise/franchisee-dealers/', FranchiseeDealerListView.as_view(), name='franchisee-dealer-list'),
    path('franchise/franchisee-dealers/<str:sort_option>/', FranchiseeDealerListView.as_view(), name='franchisee-dealer-list-sorted'),
    path('franchisee-dealers-details/<int:dealer_id>/', FranchiseeDealerDetailView.as_view(), name='franchisee-dealer-detail'),
    path('franchisee-dealer-count/', FranchiseeDealerCountView.as_view(), name='franchisee-dealer-count'),
    path('franchisee/service/add/', FranchiseeServiceAddView.as_view(), name='franchisee-service-add'),

    path('dealers/create/', DealerCreateView.as_view(), name='dealer-create'),
    path('service-providers/create/', ServiceProviderCreateView.as_view(), name='service-provider-create'),






    # path('franchise-service-providers/', FranchiseServiceProviderListView.as_view(), name='franchise-service-provider-list'),
    # path('create-sp/', ServiceProviderCreateView.as_view(), name='service-provider-create'),
    # path('add-service-provider/', AddServiceProviderView.as_view(), name='add_service_provider'),

    



]