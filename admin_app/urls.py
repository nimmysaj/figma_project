from django.urls import path,include
from admin_app.views import UserViewSet,FranchiseeViewSet,FranchiseTypeViewSet,AdManagementTypeViewSet,IncomeManagementViewSet,SMSSettingsViewSet,EmailSettingsViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'view',UserViewSet)
router.register(r'franchisees', FranchiseeViewSet) 
router.register(r'franchise_types', FranchiseTypeViewSet)
router.register(r'ad_management', AdManagementTypeViewSet)
router.register(r'income_management', IncomeManagementViewSet)
router.register(r'sms-settings', SMSSettingsViewSet)
router.register(r'email-settings', EmailSettingsViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Include all router-generated routes
]
