from django.contrib import admin
from django.urls import path
from rest_framework import routers
from django.conf.urls import include
from .views import MovieViewSet


router = routers.DefaultRouter()
router.register('movies', MovieViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
