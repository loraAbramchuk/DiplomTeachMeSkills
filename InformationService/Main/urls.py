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
    path('movies/', views.movies_list, name='movies_list'),
    path('movies/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('serials/', views.serials_list, name='serials_list'),
    path('serials/<int:pk>/', views.serial_detail, name='serial_detail'),
    path('about/', views.about, name='about'),

    path("api/", include(router.urls)),
]