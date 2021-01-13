"""General functional tests for the API endpoints."""


from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from api.v2.tests.tools import SalAPITestCase
from server.models import UserProfile


class APITest(SalAPITestCase):
    """Test the API itself."""

    api_endpoints = {
        "business_units",
        "facts",
        "inventory",
        "machine_groups",
        "machines",
        "management_sources",
        "managed_items",
        "managed_item_histories",
        "messages",
        "plugin_script_rows",
        "profiles",
        "saved_searches",
    }

    def test_access(self):
        """Test that unauthenticated requests are rejected"""
        response = self.client.get(reverse("api-root"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_options(self):
        """Ensure that API discovery is possible."""
        response = self.authed_options("api-root")
        self.assertIn("application/json", response.data["renders"])
        self.assertIn("application/json", response.data["parses"])
        self.assertIn("multipart/form-data", response.data["parses"])

    def test_api_root_get(self):
        """Test that all expected endpoints are present."""
        response = self.authed_get("api-root")
        self.assertEqual(self.api_endpoints, set(response.data.keys()))

    def test_api_docs(self):
        """Make sure the docs site is working."""
        response = self.authed_get("api-docs")
        self.assertEqual(response["content-type"], "text/html; charset=utf-8")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GASessionAuthTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = self.setup_user()
        profile = UserProfile.objects.get(pk=self.user.userprofile.id)
        profile.level = "GA"
        profile.save()

    @staticmethod
    def setup_user():
        User = get_user_model()
        return User.objects.create_user("ga_user", password="abc123")

    def test_ga_access(self):
        """Ensure GA users can use session authentication"""
        self.client.login(username="ga_user", password="abc123")
        response = self.client.get(reverse("api-root"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
