from django.urls import include, path
from .views import UnifiedView, UserCreateView,CustomerListView, SubcategoryViewSet
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
    # path('adminexpenses/', ExpensesView.as_view(), name = 'admin-payment-expenses'),
    # path('adminearnings/', EarningsView.as_view(), name = 'admin-payment-earnings'),
    # path('adsinvoices/', AdsInvoiceView.as_view(), name = 'ads-invoices'),
    # path('expensetable/', ExpenseTableView.as_view(), name= 'expense-table'),
    path('adminactions/', UnifiedView.as_view(), name='admin-actions'),
    # path('adminactions/ads/', PaginatedAdsInvoicesView.as_view(), name='paginated_ads_invoices'),
    # path('adminactions/expenses/', PaginatedExpenseTableView.as_view(), name='paginated_expense_table'),
]

    



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)