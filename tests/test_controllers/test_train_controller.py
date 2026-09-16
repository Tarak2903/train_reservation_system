from datetime import time

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.dependency import get_train_service
from app.auth import get_current_admin, get_current_user


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def service():
    return AsyncMock()


def test_get_all_trains(client, service):
    app.dependency_overrides[get_train_service] = lambda: service

    train = MagicMock()
    train.train_number = "12345"
    train.train_name = "Rajdhani"
    train.source = "Delhi"
    train.destination = "Mumbai"
    train.departure_time = time(10, 0)
    train.arrival_time = time(18, 0)

    service.get_all_trains.return_value = [train]

    response = client.get("/trains")

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Trains fetched successfully"
    assert body["data"][0]["train_number"] == "12345"
    assert body["data"][0]["train_name"] == "Rajdhani"

    service.get_all_trains.assert_awaited_once_with(None)

    app.dependency_overrides.clear()


def test_add_train(client, service):
    app.dependency_overrides[get_train_service] = lambda: service
    app.dependency_overrides[get_current_admin] = lambda: MagicMock()

    train = MagicMock()
    train.train_number = "12345"
    train.train_name = "Rajdhani"
    train.source = "Delhi"
    train.destination = "Mumbai"
    train.departure_time = time(21, 0)
    train.arrival_time = time(18, 0)

    service.add_train.return_value = train

    response = client.post(
        "/trains",
        json={
            "train_number": "12345",
            "train_name": "Rajdhani",
            "source": "Delhi",
            "destination": "Mumbai",
            "departure_time": "21:00:00",
            "arrival_time": "18:00:00"
        }
    )

    assert response.status_code == 201

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Train created successfully"
    assert body["data"]["train_number"] == "12345"
    assert body["data"]["train_name"] == "Rajdhani"

    service.add_train.assert_awaited_once()

    app.dependency_overrides.clear()


def test_get_seat_layout(client, service):
    app.dependency_overrides[get_train_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: MagicMock()

    coach = MagicMock()
    coach.id = 1
    coach.coach_number = "A01"
    coach.class_type.value = "1A"

    seat = MagicMock()
    seat.id = 100
    seat.seat_number = 1

    coach.seats = [seat]

    service.get_layout.return_value = [coach]

    response = client.get(
        "/trains/10/layout",
        params={
            "journey_date": "2026-09-20",
            "class_type": "1A"
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Seat layout retrieved successfully"

    assert body["data"][0]["coach_id"] == 1
    assert body["data"][0]["coach_number"] == "A01"
    assert body["data"][0]["class_type"] == "1A"

    assert body["data"][0]["seats"][0]["seat_id"] == 100
    assert body["data"][0]["seats"][0]["seat_number"] == 1

    service.get_layout.assert_awaited_once()

    app.dependency_overrides.clear()


def test_update_train(client, service):
    app.dependency_overrides[get_train_service] = lambda: service
    app.dependency_overrides[get_current_admin] = lambda: MagicMock()

    train = MagicMock()
    train.train_number = "12345"
    train.train_name = "Updated Rajdhani"
    train.source = "Delhi"
    train.destination = "Mumbai"
    train.departure_time = time(11, 0)
    train.arrival_time = time(19, 0)

    service.update_train.return_value = train

    response = client.patch(
        "/trains/10",
        json={
            "train_name": "Updated Rajdhani"
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Train updated successfully"
    assert body["data"]["train_name"] == "Updated Rajdhani"

    service.update_train.assert_awaited_once()

    app.dependency_overrides.clear()
