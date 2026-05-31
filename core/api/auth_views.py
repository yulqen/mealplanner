"""Custom JWT auth views with endpoint-specific throttling."""

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """JWT token obtain endpoint with strict scoped throttle."""

    throttle_scope = "token_obtain"


class ThrottledTokenRefreshView(TokenRefreshView):
    """JWT token refresh endpoint with scoped throttle."""

    throttle_scope = "token_refresh"


class ThrottledTokenVerifyView(TokenVerifyView):
    """JWT token verify endpoint with scoped throttle."""

    throttle_scope = "token_verify"
