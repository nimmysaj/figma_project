from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import ServiceRequestDetailView
from .views import UserDetailsView,UserPaymentHistoryView
from .views import dashboard_view
from .views import category_list, category_detail
from .views import TotalCountsView, RecentCustomersView, CategoriesView
from .views import ComplaintsView, IncompleteBookingsView
from .views import LoginView
from .views import StatisticsGraphView, RevenueGraphView, FinancesGraphView, CustomerArrivalGraphView, PerformanceGraphView


urlpatterns = [
    path('service-request-detail/', ServiceRequestDetailView.as_view(), name='service-request-detail'),
    path('user-details/', UserDetailsView.as_view(), name='user-details'),
    path('user-payment-history-service/', UserPaymentHistoryView.as_view(), name='user-payment-history-service'),
    path('categories/', category_list, name='category-list'),
    path('categories-detail/', category_detail, name='category-detail'),
    path('dashboard/',dashboard_view, name='dashboard'),
    path('dashboard/totals/', TotalCountsView.as_view, name='total_counts'),
    path('dashboard/recent-customers/', RecentCustomersView.as_view, name='recent_customers'),
    path('dashboard/categories/', CategoriesView.as_view, name='categories'),
    path('dashboard/complaints/', ComplaintsView.as_view, name='complaints'),
    path('dashboard/incomplete-bookings/', IncompleteBookingsView.as_view, name='incomplete_bookings'),
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/income-expense/', PerformanceGraphView.as_view(), name='admin-income-expense-month'),
    path('dashboard/compare-weekly-finances/', FinancesGraphView.as_view, name='compare_weekly_finances'),
    path('dashboard/customer-arrival/', CustomerArrivalGraphView.as_view(), name='customer-arrival'),
    path('dashboard/customer-status-totals/', StatisticsGraphView.as_view, name='customer-status-totals'),
    path('dashboard/payment-totals/', RevenueGraphView.as_view, name='payment-totals'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)