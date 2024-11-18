from django.urls import include, path
from .views import DealerListView,DealerSearchView,DealerSortView

urlpatterns = [
    path('dealer-details/', DealerListView.as_view(), name='dealer-details'),
    path('dealer-search/', DealerSearchView.as_view(), name='dealer-search'),
    path('dealer-sort/', DealerSortView.as_view(), name='dealer-sort'),
]