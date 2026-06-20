import pytest

from apps.shortener.models import ShortURL, ClickEvent
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_stats_endpoint(
    auth_client,
    user
):

    url = ShortURL.objects.create(
        owner=user,
        original_url="https://google.com"
    )

    ClickEvent.objects.create(
        short_url=url,
        ip_address="172.0.0.1",
        browser="Chrome",
        os="Windows",
        device_type="Desktop"
    )

    response = auth_client.get(
        f"/api/urls/{url.id}/stats/"
    )

    assert response.status_code == 200

    assert response.data["click_count"] == 1


@pytest.mark.django_db
def test_summary_endpoint(
    auth_client,
    user
):
    url = ShortURL.objects.create(
        owner=user,
        original_url="https://google.com"
    )

    ClickEvent.objects.create(
        short_url=url,
        ip_address="172.0.0.1",
        browser="Chrome",
        os="Windows",
        device_type="Desktop"
    )

    response = auth_client.get(
        f"/api/urls/summary/"
    )

    assert response.status_code == 200

    assert "total_urls" in response.data
    assert response.data["total_clicks"] == 1
    assert len(response.data["top_urls"]) == 1
