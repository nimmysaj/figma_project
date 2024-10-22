from django.urls import include, path
from .views import UserCreateView,CustomerListView, SubcategoryViewSet
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()
router.register(r'subcategories', SubcategoryViewSet)

urlpatterns = [
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('usersview/', CustomerListView.as_view(), name='customer-list'),
    path('', include(router.urls))

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)