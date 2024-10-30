from django.urls import path
from franchise import views

urlpatterns = [
    path('dealer/<int:pk>/',views.DealerDetailView.as_view(),name='dealer-details'),
    path('dealer/search/',views.DealerSearchView.as_view(),name='dealer-search')
]