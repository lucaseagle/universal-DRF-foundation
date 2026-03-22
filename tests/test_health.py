import datetime

import pytest
from django.conf import settings
from django.utils import timezone
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def test_health_endpoint_returns_required_fields(api_client):
    response = api_client.get("/api/health/")

    assert response.status_code == 200
    body = response.json()

    required_keys = {"status", "service", "version", "commit", "time", "checks"}
    assert required_keys.issubset(body.keys())

    assert body["status"] == "ok"
    assert body["service"] == settings.SERVICE_NAME
    assert body["version"] == settings.SERVICE_VERSION
    assert body["commit"] == settings.SERVICE_COMMIT
    assert body["checks"] == {"app": "ok", "db": "ok"}

    parsed_time = datetime.datetime.fromisoformat(body["time"])
    assert parsed_time.utcoffset() == timezone.localtime().utcoffset()


def test_health_endpoint_allows_invalid_auth_headers(api_client):
    response = api_client.get(
        "/api/health/", HTTP_AUTHORIZATION="Basic not-base64", HTTP_COOKIE="ignored"
    )

    assert response.status_code == 200


def test_health_endpoint_returns_405_for_unsupported_methods(api_client):
    response = api_client.generic(
        "TRACE", "/api/health/", HTTP_AUTHORIZATION="Basic not-base64"
    )

    assert response.status_code == 405
