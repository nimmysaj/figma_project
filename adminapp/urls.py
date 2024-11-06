from django.urls import include, path
from .views import UnifiedView, UserCreateView,CustomerListView, SubcategoryViewSet, MonthlyFinanaceReportView
# CreateRazorpayOrder, handle_payment_success,get_invoice_ids,
# from .views import ExpensesView,EarningsView,AdsInvoiceView,ExpenseTableView
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()
router.register(r'subcategories', SubcategoryViewSet)

urlpatterns = [
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('usersview/', CustomerListView.as_view(), name='customer-list'),
    path('', include(router.urls)),
    path('adminactions/', UnifiedView.as_view(), name='admin-actions'),
    path('monthly_fin_rep/', MonthlyFinanaceReportView.as_view(), name='monthly-finance-report'),
    # path('invoice_id/',get_invoice_ids, name='get-invooice-ids'),
    # path('create-order/', CreateRazorpayOrder.as_view(), name='create-razorpay-order'),
    # path('payment-success/', handle_payment_success, name='handle-payment-success')

]

    

    



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
