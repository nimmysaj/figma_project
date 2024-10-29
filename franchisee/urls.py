from django.urls import path
from .import views

urlpatterns = [
    path('submit/<uuid:pk>/', views.SubmitServiceView.as_view(), name='submit_service'),
    path('save-draft/<uuid:pk>/', views.SaveDraftServiceView.as_view(), name='save_draft_service'),
    path('delete/<uuid:pk>/', views.DeleteServiceView.as_view(), name='delete_service'),
    path('login-franchise/', views.FranchiseeLoginView.as_view(), name='franchise-login'),
]