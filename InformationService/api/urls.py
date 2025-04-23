from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GenreViewSet, CountryViewSet,
    MovieViewSet, SerialViewSet
)

router = DefaultRouter()
router.register(r'genres', GenreViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'movies', MovieViewSet)
router.register(r'serials', SerialViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
] 