from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.dependency import get_auth_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def service():
    return AsyncMock()


def test_signup(client, service):
    app.dependency_overrides[get_auth_service] = lambda: service

    user = MagicMock()
    user.id = 1
    user.user_name = "tarak"

    service.signup_user.return_value = user

    response = client.post(
        "/auth/signup",
        json={
            "name": "Tarak",
            "user_name": "tarak@GMAIL.COM",
            "password": "123456"        }
    )

    assert response.status_code == 201
    assert response.json()["success"] is True

    app.dependency_overrides.clear()


def test_login(client, service):
    app.dependency_overrides[get_auth_service] = lambda: service

    service.login_user.return_value = "token123"

    response = client.post(
        "/auth/login",
        data={
            "username": "tarak",
            "password": "123456"
        }
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["access_token"] == "token123"

    app.dependency_overrides.clear()