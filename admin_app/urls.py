from django.contrib import admin
from django.urls import path
from admin_app.views import Franchise_TypeView, Service_HistoryView#, FranchiseeDetailsView

urlpatterns = [
    path("ftype/", Franchise_TypeView.as_view()),
    path("shistory/", Service_HistoryView.as_view()),
    #path("frdet/", FranchiseeDetailsView.as_view())
]