from django.urls import path
from .views import (
    CategoryListView, 
    CategoryDetailView, 
    SubCategoryListCreateView, 
    SubCategoryDetailView, 
    SearchView,
    ServiceTypeListCreateView, 
    ServiceTypeDetailView, 
    CollarListCreateView,
    CollarDetailView,
    ServiceProviderListCreateView, 
    ServiceProviderDetailView,
)

urlpatterns = [
    # Category endpoints
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    # Sub-category endpoints
    path('categories/<int:category_id>/subcategories/', SubCategoryListCreateView.as_view(), name='subcategory-list'),
    path('categories/<int:category_id>/subcategories/<int:pk>/', SubCategoryDetailView.as_view(), name='subcategory-detail'),

    # Search
    path('search/', SearchView.as_view(), name='search'),

    # Routes for Service_Type
    path('service_types/', ServiceTypeListCreateView.as_view(), name='service-type-list-create'),
    path('service_types/<int:pk>/', ServiceTypeDetailView.as_view(), name='service-type-detail'),

    # Routes for Collar
    path('collars/', CollarListCreateView.as_view(), name='collar-list-create'),
    path('collars/<int:pk>/', CollarDetailView.as_view(), name='collar-detail'),

    # Service Provider
    path('sp/', ServiceProviderListCreateView.as_view(), name='service-provider-list-create'),
    path('sp/<int:pk>/', ServiceProviderDetailView.as_view(), name='service-provider-detail'),
    
]
