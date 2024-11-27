from django.urls import include, path
from .views import UnifiedView, UserCreateView,CustomerListView, SubcategoryViewSet, MonthlyFinanaceReportView, InvoiceOthersAddView, get_or_update_othertype_admin_invoices,get_customer_count, get_online_customer_count, get_total_service_request, get_leadrequest_count
from .views import get_total_complaints_count, get_active_services_count, IncomeManagementPostView, IncomeMgmtGetView, IncomeMgmtUpdateView
# CreateRazorpayOrder, handle_payment_success,get_invoice_ids,get_othertype_admin_invoices,, get_active_services_count
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
    path('customer_count/', get_customer_count,name='customer_count'),
    path('online_customer_count/', get_online_customer_count, name = 'active_customer_count'),
    path('total_service_request/', get_total_service_request, name='total_service_request'),
    path('lead_request_count/', get_leadrequest_count, name = 'leadrequest_count'),
    path('active_services/', get_active_services_count, name='active_services'),
    path('get_total_complaints_count/', get_total_complaints_count, name = 'get_total_complaints_count'),
    path('adminactions/', UnifiedView.as_view(), name='admin-actions'),          
    path('monthly_fin_rep/', MonthlyFinanaceReportView.as_view(), name='monthly-finance-report'),
    path('invoice_type_others/', InvoiceOthersAddView.as_view(), name='invoice-others'),
    path('get_or_update_othertype_admin_invoices/', get_or_update_othertype_admin_invoices, name='invoice-othertype-get'),
    path('IncomeManagementPost/', IncomeManagementPostView.as_view(), name='IncomeManagementPost'),
    path('IncomeMgmtGet/', IncomeMgmtGetView.as_view(), name='IncomeMgmtGet'),
    path('IncomeMgmtUpdate/', IncomeMgmtUpdateView.as_view(), name='IncomeMgmtUpdate')
    # path('update_invoice/', update_invoice, name='update_invoice'),
    # path('invoice_id/',get_invoice_ids, name='get-invooice-ids'),
    # path('create-order/', CreateRazorpayOrder.as_view(), name='create-razorpay-order'),
    # path('payment-success/', handle_payment_success, name='handle-payment-success')

]

    

    



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
