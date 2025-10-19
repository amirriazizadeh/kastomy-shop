
from django.urls import path
from .views import ProductAPIView, ProductDetailAPIView,ProductReviewListView

urlpatterns = [
    path('products/', ProductAPIView.as_view(), name='product-list-create'),
    path('products/<str:id>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path("products/<int:product_id>/review_list/", ProductReviewListView.as_view(), name="product-review-list"),
]

