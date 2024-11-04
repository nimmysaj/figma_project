from django.urls import include, path
from .views import DealerView,DealerSearchView

urlpatterns = [
    path('dealer-details/', DealerView.as_view(), name='dealer-details'),
    path('dealer-search/', DealerSearchView.as_view(), name='dealer-search'),
]