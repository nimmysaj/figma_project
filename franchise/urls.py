from django.urls import include, path
from .views import FranchiseeLoginView,DealerView,DealerSearchView

urlpatterns = [
    path('login/', FranchiseeLoginView.as_view(), name='franchisee_login'),
    path('dealer-details/', DealerView.as_view(), name='dealer-details'),
    path('dealer-search/', DealerSearchView.as_view(), name='dealer-search'),
]