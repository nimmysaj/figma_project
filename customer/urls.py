from django.urls import path
from .views import GetCategoriesView


urlpatterns = [path('categories/',GetCategoriesView.as_view(),name='categories')
]