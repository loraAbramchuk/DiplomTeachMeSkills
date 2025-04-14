from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import GenreViewSet, CountryViewSet

router = DefaultRouter()
router.register(r'genres', GenreViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'movies', views.MovieViewSet, basename='movies')
router.register(r'serials', views.SerialViewSet, basename='serials')

urlpatterns = [
    path("", views.index, name="index"),

    path("api/", include(router.urls)),
]