from django.urls import path
from Admin import views

urlpatterns = [
    path('add/newuser/',views.AddNewUserView.as_view(),name='add-user'),
    path('dashboard/',views.AdminDashBoardView.as_view(),name='admin-dashboard'),
    path('incomplete-booking/',views.IncompleteBookingView.as_view(),name='incomplete-booking'),
    path('complaints/',views.ComplaintsView.as_view(),name='complaints'),
    path('ads/',views.AdsManagementDashBoardView.as_view())
]