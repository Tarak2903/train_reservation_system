from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.dependency import get_coach_service
from app.auth import get_current_admin


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def service():
    return AsyncMock()


def test_get_coaches_by_train_number(client, service):
    app.dependency_overrides[get_coach_service] = lambda: service

    coach = MagicMock()
    coach.coach_number = "A01"
    coach.class_type = "1A"
    coach.total_seat_capacity = 20
    coach.rac_capacity = 5

    service.get_coaches_by_train_number.return_value = [coach]

    response = client.get("/trains/12345/coaches")

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Coaches fetched successfully"
    assert body["data"][0]["coach_number"] == "A01"
    assert body["data"][0]["total_seat_capacity"] == 20
    assert body["data"][0]["rac_capacity"] == 5

    service.get_coaches_by_train_number.assert_awaited_once_with(12345)

    app.dependency_overrides.clear()


def test_add_train_coach(client, service):
    app.dependency_overrides[get_coach_service] = lambda: service
    app.dependency_overrides[get_current_admin] = lambda: MagicMock()

    coach = MagicMock()
    coach.coach_number = "A01"
    coach.class_type.value = "1A"
    coach.total_seat_capacity = 20
    coach.rac_capacity = 5

    service.add_coach.return_value = coach

    response = client.post(
        "/trains/10/coaches",
        json={
            "coach_number": "A01",
            "class_type": "1A",
            "total_seat_capacity": 20,
            "rac_capacity": 5
        }
    )

    assert response.status_code == 201

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Coach added successfully"
    assert body["data"]["coach_number"] == "A01"
    assert body["data"]["class_type"] == "1A"

    service.add_coach.assert_awaited_once()

    app.dependency_overrides.clear()


def test_update_coach(client, service):
    app.dependency_overrides[get_coach_service] = lambda: service
    app.dependency_overrides[get_current_admin] = lambda: MagicMock()

    coach = MagicMock()

    service.update_coach.return_value = coach

    response = client.patch(
        "/10/coaches/20",
        json={
            "coach_number": "A02",
            "class_type": "2A",
            "total_seat_capacity": 30,
            "rac_capacity": 5
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Coach updated successfully"

    service.update_coach.assert_awaited_once()

    app.dependency_overrides.clear()
