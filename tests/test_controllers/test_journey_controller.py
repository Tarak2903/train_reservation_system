from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.dependency import get_journey_service
from app.auth import get_current_admin


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def service():
    return AsyncMock()


def test_add_train_journey(client, service):
    app.dependency_overrides[get_journey_service] = lambda: service
    app.dependency_overrides[get_current_admin] = lambda: MagicMock()

    journey = MagicMock()
    journey.id = 1
    journey.train_id = 10
    journey.journey_date = "2026-09-20"

    service.add_journey.return_value = journey

    response = client.post(
        "/trains/10/journeys",
        json={
            "journey_date": "2026-09-20"
        }
    )

    assert response.status_code == 201

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Train journey added successfully"
    assert body["data"]["journey_id"] == 1
    assert body["data"]["train_id"] == 10
    assert body["data"]["journey_date"] == "2026-09-20"

    service.add_journey.assert_awaited_once()

    app.dependency_overrides.clear()
