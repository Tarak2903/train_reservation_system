from datetime import date
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth import get_current_user
from app.controller.BookingController import router
from app.dependency import get_booking_service
from app.models.enums import (
    BookingStatus,
    CoachClass,
    PassengerStatus,
    Role,
)
from app.models.schemas.user import User


class TestBookingController:

    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(router)

        self.client = TestClient(self.app)
        self.service = AsyncMock()

        self.user = User(
            id=1,
            name="John",
            user_name="john@test.com",
            password="secret",
            role=Role.USER,
        )

        self.app.dependency_overrides[get_booking_service] = (
            lambda: self.service
        )

        self.app.dependency_overrides[get_current_user] = (
            lambda: self.user
        )

    def make_booking(self):
        booking = MagicMock()

        booking.pnr = "ABC123"
        booking.train_id = 10
        booking.journey_date = date(2026, 9, 15)
        booking.class_type = CoachClass.SLEEPER
        booking.status = BookingStatus.ACTIVE
        booking.user_id = 1

        passenger = MagicMock()

        passenger.passenger.name = "Passenger One"
        passenger.status = PassengerStatus.CNF
        passenger.queue_sequence = None

        passenger.seat.seat_number = 15
        passenger.seat.coach.coach_number = "S1"

        booking.passengers = [passenger]

        return booking

    def test_book_ticket(self):
        booking = self.make_booking()

        self.service.book_ticket.return_value = (
            booking,
            "Ticket booked successfully",
        )

        response = self.client.post(
            "/bookings",
            json={
                "train_id": 10,
                "journey_date": "2026-09-15",
                "class_type": "SL",
                "booking_status": "CNF",
                "passenger_ids": [2],
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["success"] is True
        assert body["message"] == "Ticket booked successfully"

        assert body["data"]["pnr"] == "ABC123"
        assert body["data"]["train_id"] == 10
        assert body["data"]["journey_date"] == "2026-09-15"
        assert body["data"]["class_type"] == "SL"
        assert body["data"]["booking_status"] == "ACTIVE"
        assert body["data"]["booked_by"] == 1

        assert body["data"]["passengers"] == [
            {
                "passenger_name": "Passenger One",
                "status": "CNF",
                "queue_sequence": None,
                "coach_number": "S1",
                "seat_number": 15,
            }
        ]

        self.service.book_ticket.assert_awaited_once()

        args = self.service.book_ticket.await_args.args

        assert args[0].train_id == 10
        assert args[0].journey_date == date(2026, 9, 15)
        assert args[0].class_type == CoachClass.SLEEPER
        assert args[0].booking_status == PassengerStatus.CNF
        assert args[0].passenger_ids == [2]
        assert args[1] == 1

    def test_cancel_ticket(self):
        booking = self.make_booking()

        self.service.cancel_ticket.return_value = booking

        response = self.client.delete("/bookings/100")

        assert response.status_code == 200

        body = response.json()

        assert body["success"] is True
        assert body["message"] == "Ticket cancelled successfully"
        assert body["data"]["pnr"] == "ABC123"

        self.service.cancel_ticket.assert_awaited_once_with(
            100,
            1,
        )

    def test_get_booking_status(self):
        booking = self.make_booking()

        self.service.get_booking_status.return_value = booking

        response = self.client.get("/bookings/100")

        assert response.status_code == 200

        body = response.json()

        assert body["success"] is True
        assert body["message"] == "Booking details retrieved successfully"

        assert body["data"]["pnr"] == "ABC123"
        assert body["data"]["train_id"] == 10
        assert body["data"]["journey_date"] == "2026-09-15"
        assert body["data"]["class_type"] == "SL"
        assert body["data"]["booking_status"] == "ACTIVE"
        assert body["data"]["booked_by"] == 1

        self.service.get_booking_status.assert_awaited_once_with(
            100,
            1,
        )

    def test_get_availability(self):
        self.service.get_availability.return_value = {
            "train_id": 10,
            "journey_date": date(2026, 9, 15),
            "class_type": "SL",
            "total_seats": 72,
            "confirmed": 50,
            "available": 22,
            "rac_capacity": 6,
            "rac": 2,
            "waitlist": 0,
        }

        response = self.client.get(
            "/availability",
            params={
                "train_id": 10,
                "journey_date": "2026-09-15",
                "class_type": "SL",
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["success"] is True
        assert body["message"] == "Availability retrieved successfully"

        assert body["data"] == {
            "train_id": 10,
            "journey_date": "2026-09-15",
            "class_type": "SL",
            "total_seats": 72,
            "confirmed": 50,
            "available": 22,
            "rac_capacity": 6,
            "rac": 2,
            "waitlist": 0,
        }

        self.service.get_availability.assert_awaited_once_with(
            10,
            date(2026, 9, 15),
            CoachClass.SLEEPER,
        )