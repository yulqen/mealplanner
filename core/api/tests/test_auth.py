"""
Tests for API authentication.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework import status

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
