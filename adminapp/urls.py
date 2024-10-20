from django.urls import path
from .views import ServiceRequestDetailView
from .views import UserDetailsView,UserPaymentHistoryView
from .views import category_list, category_detail
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('service-request-detail/', ServiceRequestDetailView.as_view(), name='service-request-detail'),
    path('user-details/', UserDetailsView.as_view(), name='user-details'),
    path('user-payment-history-service/', UserPaymentHistoryView.as_view(), name='user-payment-history-service'),
    path('categories/', category_list, name='category-list'),
    path('categories/<int:pk>/', category_detail, name='category-detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)