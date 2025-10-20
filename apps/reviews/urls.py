from django.urls import path
from .views import (
    ProductReviewListView,
    StoreReviewListView,
    ProductReviewCreateView,
    StoreReviewCreateView,
)

urlpatterns = [
    path(
        "products/<int:product_id>/review_list/",
        ProductReviewListView.as_view(),
        name="product-reviews",
    ),
    path(
        "products/<int:product_id>/reviews_create/",
        ProductReviewCreateView.as_view(),
        name="product-review-create",
    ),
    path(
        "stores/<int:store_id>/review_list/",
        StoreReviewListView.as_view(),
        name="store-reviews",
    ),
    path(
        "stores/<int:store_id>/reviews_create/",
        StoreReviewCreateView.as_view(),
        name="store-review-create",
    ),
]
