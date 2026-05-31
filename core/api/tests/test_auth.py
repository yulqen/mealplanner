"""
Tests for API authentication.

Tests both session-based and token-based (JWT) authentication methods.
"""

import importlib

from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import clear_url_caches
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class APIAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access API endpoints."""
        # Try to access an API endpoint without authentication
        response = self.client.get("/api/v1/meal-types/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(b"Authentication credentials were not provided", response.content)

    def test_authenticated_access_allowed(self):
        """Test that authenticated users can access API endpoints."""
        # Login first
        login_response = self.client.post(
            "/accounts/login/",
            {"username": "testuser", "password": "testpass123"},
        )
        self.assertEqual(login_response.status_code, status.HTTP_302_FOUND)
        
        # Now access API endpoint
        response = self.client.get("/api/v1/meal-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_session_authentication(self):
        """Test that session authentication works for API endpoints."""
        # Login
        self.client.login(username="testuser", password="testpass123")
        
        # Access API endpoint
        response = self.client.get("/api/v1/recipes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_endpoints_require_authentication(self):
        """Test that all API endpoints require authentication."""
        # Login
        self.client.login(username="testuser", password="testpass123")
        
        # Test various endpoints
        endpoints = [
            "/api/v1/meal-types/",
            "/api/v1/shopping-categories/",
            "/api/v1/stores/",
            "/api/v1/ingredients/",
            "/api/v1/recipes/",
            "/api/v1/week-plans/",
            "/api/v1/planned-meals/",
            "/api/v1/shopping-lists/",
            "/api/v1/shopping-list-items/",
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Endpoint {endpoint} should be accessible with authentication",
            )


class TokenAuthenticationTests(TestCase):
    """Tests for JWT token-based authentication."""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="tokenuser",
            password="tokenpass123",
        )

    def test_token_obtain_pair(self):
        """Test obtaining access and refresh tokens."""
        response = self.client.post(
            "/api/v1/token/",
            {"username": "tokenuser", "password": "tokenpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_obtain_pair_invalid_credentials(self):
        """Test token obtain with invalid credentials."""
        response = self.client.post(
            "/api/v1/token/",
            {"username": "tokenuser", "password": "wrongpassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_token_authentication(self):
        """Test that access token authenticates API requests."""
        # Get token
        token_response = self.client.post(
            "/api/v1/token/",
            {"username": "tokenuser", "password": "tokenpass123"},
            format="json",
        )
        access_token = token_response.data["access"]
        
        # Use token to access API
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get("/api/v1/meal-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_token_rotation_invalidates_old_refresh_token(self):
        """Test refresh rotation invalidates the previously used refresh token."""
        # Get initial tokens
        token_response = self.client.post(
            "/api/v1/token/",
            {"username": "tokenuser", "password": "tokenpass123"},
            format="json",
        )
        refresh_token = token_response.data["refresh"]

        # First refresh should succeed and rotate token
        refresh_response = self.client.post(
            "/api/v1/token/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)
        self.assertIn("refresh", refresh_response.data)

        # Reusing the old refresh token should now fail
        reuse_response = self.client.post(
            "/api/v1/token/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(reuse_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_invalid(self):
        """Test refreshing with invalid refresh token."""
        response = self.client.post(
            "/api/v1/token/refresh/",
            {"refresh": "invalid.token.here"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_verify_valid(self):
        """Test verifying a valid token."""
        # Get token
        token_response = self.client.post(
            "/api/v1/token/",
            {"username": "tokenuser", "password": "tokenpass123"},
            format="json",
        )
        access_token = token_response.data["access"]
        
        # Verify token
        verify_response = self.client.post(
            "/api/v1/token/verify/",
            {"token": access_token},
            format="json",
        )
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

    def test_token_verify_invalid(self):
        """Test verifying an invalid token."""
        response = self.client.post(
            "/api/v1/token/verify/",
            {"token": "invalid.token.here"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_all_endpoints_with_token_auth(self):
        """Test that all API endpoints work with token authentication."""
        # Get token
        token_response = self.client.post(
            "/api/v1/token/",
            {"username": "tokenuser", "password": "tokenpass123"},
            format="json",
        )
        access_token = token_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        
        # Test various endpoints
        endpoints = [
            "/api/v1/meal-types/",
            "/api/v1/shopping-categories/",
            "/api/v1/stores/",
            "/api/v1/ingredients/",
            "/api/v1/recipes/",
            "/api/v1/week-plans/",
            "/api/v1/planned-meals/",
            "/api/v1/shopping-lists/",
            "/api/v1/shopping-list-items/",
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Endpoint {endpoint} should be accessible with token authentication",
            )

    def test_token_auth_with_custom_actions(self):
        """Test token authentication with custom API actions."""
        # Get token
        token_response = self.client.post(
            "/api/v1/token/",
            {"username": "tokenuser", "password": "tokenpass123"},
            format="json",
        )
        access_token = token_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        
        # Test that authenticated token user can access endpoints
        response = self.client.get("/api/v1/recipes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class APIDocsExposureTests(TestCase):
    """Tests for production-safe docs endpoint exposure controls."""

    def test_schema_endpoints_disabled_when_docs_off(self):
        with override_settings(API_DOCS_ENABLED=False):
            clear_url_caches()
            import mealplanner.urls

            importlib.reload(mealplanner.urls)

            client = Client()
            schema_response = client.get("/api/v1/schema/")
            swagger_response = client.get("/api/v1/schema/swagger-ui/")

            self.assertEqual(schema_response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(swagger_response.status_code, status.HTTP_404_NOT_FOUND)

        clear_url_caches()
        import mealplanner.urls

        importlib.reload(mealplanner.urls)


class APIThrottleTests(TestCase):
    """Tests for API throttling behaviour."""

    def test_token_obtain_is_rate_limited(self):
        cache.clear()
        User.objects.create_user(username="throttleuser", password="throttlepass123")
        client = APIClient()

        payload = {"username": "throttleuser", "password": "throttlepass123"}

        responses = [client.post("/api/v1/token/", payload, format="json") for _ in range(11)]

        self.assertTrue(all(r.status_code == status.HTTP_200_OK for r in responses[:10]))
        self.assertEqual(responses[10].status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class DualAuthenticationTests(TestCase):
    """Tests to verify both session and token authentication work."""

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="dualuser",
            password="dualpass123",
        )

    def test_session_and_token_both_work(self):
        """Test that both session and token auth methods work for the same user."""
        # Test session authentication
        session_client = Client()
        session_client.login(username="dualuser", password="dualpass123")
        session_response = session_client.get("/api/v1/meal-types/")
        self.assertEqual(session_response.status_code, status.HTTP_200_OK)
        
        # Test token authentication
        token_client = APIClient()
        token_response = token_client.post(
            "/api/v1/token/",
            {"username": "dualuser", "password": "dualpass123"},
            format="json",
        )
        access_token = token_response.data["access"]
        token_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        token_response = token_client.get("/api/v1/meal-types/")
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_fails_for_both_methods(self):
        """Test that unauthenticated requests fail regardless of auth method."""
        # Test without session
        session_client = Client()
        session_response = session_client.get("/api/v1/meal-types/")
        self.assertEqual(session_response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test without token
        token_client = APIClient()
        token_response = token_client.get("/api/v1/meal-types/")
        self.assertEqual(token_response.status_code, status.HTTP_403_FORBIDDEN)
