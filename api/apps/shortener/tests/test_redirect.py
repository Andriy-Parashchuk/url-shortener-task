import pytest

from apps.shortener.models import ShortURL
from django.contrib.auth.models import User

from apps.shortener.models import ClickEvent


@pytest.mark.django_db
def test_redirect_returns_302(
    client,
    user
):

    url = ShortURL.objects.create(
        owner=user,
        original_url="https://google.com",
        short_code="abc123"
    )

    response = client.get(
        "/abc123"
    )

    assert response.status_code == 302

    assert response.url == "https://google.com"


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
        ip_address='172.0.0.1',
        browser="Chrome",
        os="Windows",
        device_type="Desktop"
    )

    response = auth_client.get(
        f"/api/urls/{url.id}/stats/"
    )

    assert response.status_code == 200
    assert response.data["click_count"] == 1
