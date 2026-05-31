from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.api.auth_views import (
    ThrottledTokenObtainPairView,
    ThrottledTokenRefreshView,
    ThrottledTokenVerifyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    # API v1
    path("api/v1/", include("core.api.urls")),
    # JWT Token endpoints
    path("api/v1/token/", ThrottledTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", ThrottledTokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", ThrottledTokenVerifyView.as_view(), name="token_verify"),
    path("", include("core.urls")),
]

if settings.API_DOCS_ENABLED:
    urlpatterns += [
        # drf-spectacular schema URLs
        path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/v1/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
    ]
