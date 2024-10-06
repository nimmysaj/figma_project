from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FranchiseeViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'franchisees', FranchiseeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]