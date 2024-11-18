from django.urls import path
from .views import FranchiseeListView, CategoryListView

urlpatterns = [
    path('franchisees-list/', FranchiseeListView.as_view(), name='franchisee-list'),
    path('categories-list/', CategoryListView.as_view(), name='category-list'),
]