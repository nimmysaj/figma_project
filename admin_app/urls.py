from django.urls import path,include
from admin_app.views import UserViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'view',UserViewSet)

urlpatterns = [
    path('view/',UserViewSet.as_view({'get':'list','patch':'update'}),name='admin_app'),
    # path('view/',include(router.urls))

]+router.urls