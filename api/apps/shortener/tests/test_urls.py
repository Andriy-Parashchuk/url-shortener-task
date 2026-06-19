import pytest

from apps.shortener.models import ShortURL
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_create_short_url(auth_client):

    response = auth_client.post(
        "/api/urls/",
        {
            "original_url": "https://google.com"
        },
        format="json"
    )

    assert response.status_code == 201

    assert ShortURL.objects.count() == 1


@pytest.mark.django_db
def test_short_code_generated(auth_client):

    response = auth_client.post(
        "/api/urls/",
        {
            "original_url": "https://google.com"
        },
        format="json"
    )

    url = ShortURL.objects.first()

    assert url.short_code is not None
    assert len(url.short_code) > 0


@pytest.mark.django_db
def test_user_sees_only_own_urls(
    auth_client,
    user
):

    another_user = User.objects.create_user(
        username="another",
        password="123"
    )

    ShortURL.objects.create(
        owner=user,
        original_url="https://google.com"
    )

    ShortURL.objects.create(
        owner=another_user,
        original_url="https://github.com"
    )

    response = auth_client.get(
        "/api/urls/"
    )

    assert len(response.data) == 1


@pytest.mark.django_db
def test_url_list_no_n_plus_one(
    auth_client,
    user,
    django_assert_num_queries
):

    for i in range(20):
        ShortURL.objects.create(
            owner=user,
            original_url=f"https://site{i}.com"
        )

    with django_assert_num_queries(1):
        response = auth_client.get("/api/urls/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthorized_user_cannot_access_urls(
    api_client
):

    response = api_client.get(
        "/api/urls/"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthorized_user_cannot_create_url(
    api_client
):

    response = api_client.post(
        "/api/urls/",
        {
            "original_url": "https://google.com"
        },
        format="json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_get_one_url_detail(
    auth_client,
    user
):

    url = ShortURL.objects.create(
        owner=user,
        original_url="https://google.com"
    )

    response = auth_client.get(
        f"/api/urls/{url.id}/"
    )

    assert response.status_code == 200
    assert response.data["original_url"] == "https://google.com"
    assert "click_count" in response.data
    assert "recent_clicks" in response.data


@pytest.mark.django_db
def test_delete_own_url(
    auth_client,
    user
):

    url = ShortURL.objects.create(
        owner=user,
        original_url="https://google.com"
    )

    response = auth_client.delete(
        f"/api/urls/{url.id}/"
    )

    assert response.status_code == 204


@pytest.mark.django_db
def test_cannot_delete_foreign_url(
    auth_client
):

    another_user = User.objects.create_user(
        username="another"
    )

    url = ShortURL.objects.create(
        owner=another_user,
        original_url="https://google.com"
    )

    response = auth_client.delete(
        f"/api/urls/{url.id}/"
    )

    assert response.status_code == 404



