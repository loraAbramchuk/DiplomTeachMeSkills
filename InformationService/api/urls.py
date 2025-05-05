from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views
from .schema import schema_view

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'genres', views.GenreViewSet)
router.register(r'countries', views.CountryViewSet)
router.register(r'movies', views.MovieViewSet)
router.register(r'serials', views.SerialViewSet)
router.register(r'reviews', views.ReviewViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] 