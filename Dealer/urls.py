from django.urls import path
from Dealer import views

urlpatterns = [
    path('serviceprovider/verification/',views.ServiceProviderVerificationListView.as_view()),
    path('login/',views.DealerLoginView.as_view(),name='dealer_login')
]