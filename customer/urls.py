from django.urls import path
from .views import GetCategoriesView,GetSubcategoryView


urlpatterns = [
    path('categories/',GetCategoriesView.as_view(),name='categories'),
    path('subcategories/',GetSubcategoryView.as_view(),name='subcategories'),
               
]