from django.urls import path,include
from admin_app.views import UserViewSet,FranchiseeViewSet,FranchiseTypeViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'view',UserViewSet)
router.register(r'franchisees', FranchiseeViewSet) 
router.register(r'franchise_types', FranchiseTypeViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Include all router-generated routes
]
