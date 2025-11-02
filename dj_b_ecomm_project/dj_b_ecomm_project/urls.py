
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path("rosetta/", include("rosetta.urls")),
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('shop/', include('apps.shop.urls')),
    path('orders/', include('apps.orders.urls')),
    path('accounts/', include('allauth.urls')),
  

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
