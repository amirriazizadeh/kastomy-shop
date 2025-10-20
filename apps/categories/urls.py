from django.urls import path
from apps.categories.views import CategoryListView, CategoryDetailView

urlpatterns = [
    path("", CategoryListView.as_view(), name="category_list"),
    path("<int:pk>/", CategoryDetailView.as_view(), name="category_detail"),
]