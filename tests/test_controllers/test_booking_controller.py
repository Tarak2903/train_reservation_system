from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.dependency import get_booking_service
from app.auth import get_current_user


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def service():
    return AsyncMock()


def test_book_ticket(client, service):
    app.dependency_overrides[get_booking_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: MagicMock(id=1)

    booking = MagicMock()

    booking.pnr = "PNR123"
    booking.train_id = 10
    booking.journey_date = "2026-09-20"
    booking.class_type.value = "SL"
    booking.status.value = "ACTIVE"
    booking.user_id = 1

    passenger = MagicMock()
    passenger.passenger.name = "Tarak"
    passenger.status.value = "CNF"
    passenger.queue_sequence = None

    passenger.seat = MagicMock()
    passenger.seat.seat_number = 1
    passenger.seat.coach.coach_number = "S01"

    booking.passengers = [passenger]

    service.book_ticket.return_value = (
        booking,
        "Ticket booked successfully"
    )

    response = client.post(
        "/bookings",
        json={
            "train_id": 10,
            "journey_date": "2026-09-20",
            "class_type": "SL",
            "booking_status": "CNF",
            "passenger_ids": [2]
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Ticket booked successfully"

    assert body["data"]["pnr"] == "PNR123"
    assert body["data"]["train_id"] == 10
    assert body["data"]["class_type"] == "SL"
    assert body["data"]["booking_status"] == "ACTIVE"
    assert body["data"]["booked_by"] == 1

    assert body["data"]["passengers"][0]["passenger_name"] == "Tarak"
    assert body["data"]["passengers"][0]["status"] == "CNF"
    assert body["data"]["passengers"][0]["coach_number"] == "S01"
    assert body["data"]["passengers"][0]["seat_number"] == 1

    service.book_ticket.assert_awaited_once()

    app.dependency_overrides.clear()


def test_cancel_ticket(client, service):
    app.dependency_overrides[get_booking_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: MagicMock(id=1)

    booking = MagicMock()

    booking.pnr = "PNR123"
    booking.train_id = 10
    booking.journey_date = "2026-09-20"
    booking.class_type.value = "SL"
    booking.status.value = "CANCELLED"
    booking.user_id = 1
    booking.passengers = []

    service.cancel_ticket.return_value = booking

    response = client.delete("/bookings/10")

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Ticket cancelled successfully"
    assert body["data"]["pnr"] == "PNR123"
    assert body["data"]["booking_status"] == "CANCELLED"

    service.cancel_ticket.assert_awaited_once_with(10, 1)

    app.dependency_overrides.clear()


def test_get_booking_status(client, service):
    app.dependency_overrides[get_booking_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: MagicMock(id=1)

    booking = MagicMock()

    booking.pnr = "PNR123"
    booking.train_id = 10
    booking.journey_date = "2026-09-20"
    booking.class_type.value = "SL"
    booking.status.value = "ACTIVE"
    booking.user_id = 1
    booking.passengers = []

    service.get_booking_status.return_value = booking

    response = client.get("/bookings/10")

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Booking details retrieved successfully"
    assert body["data"]["pnr"] == "PNR123"

    service.get_booking_status.assert_awaited_once_with(10, 1)

    app.dependency_overrides.clear()


def test_get_availability(client, service):
    app.dependency_overrides[get_booking_service] = lambda: service

    service.get_availability.return_value = {
        "train_id": 10,
        "journey_date": "2026-09-20",
        "class_type": "SL",
        "total_seats": 100,
        "confirmed": 50,
        "available": 50,
        "rac_capacity": 20,
        "rac": 5,
        "waitlist": 2
    }

    response = client.get(
        "/train/10/availability",
        params={
            "journey_date": "2026-09-20",
            "class_type": "SL"
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Availability retrieved successfully"

    assert body["data"]["train_id"] == 10
    assert body["data"]["journey_date"] == "2026-09-20"
    assert body["data"]["class_type"] == "SL"
    assert body["data"]["total_seats"] == 100
    assert body["data"]["confirmed"] == 50
    assert body["data"]["available"] == 50
    assert body["data"]["rac_capacity"] == 20
    assert body["data"]["rac"] == 5
    assert body["data"]["waitlist"] == 2

    service.get_availability.assert_awaited_once()

    app.dependency_overrides.clear()
