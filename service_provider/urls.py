from django.urls import path
from .views import (
    CategoryListView, 
    SubCategoryListCreateView, 
    SearchView,
    ServiceProviderListCreateView, 
    CreateComplaintView
)

urlpatterns = [
    # Category endpoints
    path('categories/', CategoryListView.as_view(), name='category-list'),

    # Sub-category endpoints
    path('categories/<int:category_id>/subcategories/', SubCategoryListCreateView.as_view(), name='subcategory-list'),

    # Search
    path('search/', SearchView.as_view(), name='search'),

    # Service Provider
    path('sp/', ServiceProviderListCreateView.as_view(), name='service-provider-list-create'),

    # Complaint Form
    path('complaint/', CreateComplaintView.as_view(), name='create-complaint'),
    
]
