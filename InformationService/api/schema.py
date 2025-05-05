from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Information Service API",
        default_version='v1',
        description="API для информационного сервиса",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="larachka.06@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
) 