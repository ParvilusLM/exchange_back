from django.contrib import auth
from django.urls import path
from django.urls import include, path
from django.conf import settings
from rest_framework import routers
from  .views import *

app_name = 'exchangeApi'

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'utilisateurs', UserViewSet, basename='utilisateurs')
router.register(r'taux-de-change', TauxDeChangeViewSet, basename='taux-de-change')
router.register(r'conversions', ConversionDeDeviseViewSet, basename='conversion')
router.register(r'historiques', HistoriqueTauxDeChangeViewSet, basename='historique')

urlpatterns=[
	path('api/', include(router.urls)),
	path('api-auth/', obtain_auth_token),
]