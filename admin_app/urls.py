from django.contrib import admin
from django.urls import path
from admin_app.views import *

urlpatterns = [
    path("ftype/", Franchise_TypeView.as_view()),
    path("shistory/", Service_HistoryView.as_view()),
    path("frdet/", FranchiseeDetailsView.as_view()),
    path("adadd/", AdListView.as_view()),
    #path("rzrpay/", RazorpayPaymentView.as_view()),
]