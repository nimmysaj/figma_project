from django.urls import path
from .views import CustomerServiceRequestsView, FranchiseeListView, CategoryListView
from django.urls import path
from Admin import views

urlpatterns = [
    path('customer/<int:servicerequest_id>/service-requests/', CustomerServiceRequestsView.as_view(), name='customer-service-requests'),
    path('add/newuser/',views.AddNewUserView.as_view(),name='add-user'),
    path('dashboard/',views.AdminDashBoardView.as_view(),name='admin-dashboard'),
    path('incomplete-booking/',views.IncompleteBookingView.as_view(),name='incomplete-booking'),
    path('complaints/',views.ComplaintsView.as_view(),name='complaints'),
    path('ads/',views.AdsManagementDashBoardView.as_view()),
    path('ads-category/',views.AdsCategoryView.as_view()),
    path('ads-management/',views.AdsManagementView.as_view()),
    path('franchisees-list/', FranchiseeListView.as_view(), name='franchisee-list'),
    path('categories-list/', CategoryListView.as_view(), name='category-list'),
]
