

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    #accounts
    path('api/accounts/', include('accounts.urls')),
    path('api/myuser/',include('accounts.urls_myuser')),
    #product
    path('api/product/',include('products.urls')),
    path('api/categories/',include('products.urls_categories')),
    # cart
    path('api/mycart/', include('cart.urls')),
    # order
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('orders.urls_payments')),
     # API Schema:
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)