
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('',include('exchangeApi.urls')),
    path('admin/', admin.site.urls),
    path('api-doc/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api-doc/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema')), 
]
