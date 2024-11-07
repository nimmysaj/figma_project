from django.urls import path
from .views import FranchiseeListView

urlpatterns = [
    path('franchisees-list/', FranchiseeListView.as_view(), name='franchisee-list'),
]