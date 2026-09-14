from datetime import date
from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth import get_current_admin, get_current_user
from app.controller.TrainController import router
from app.dependency import get_train_service
from app.models.enums import CoachClass, Role
from app.models.schemas.coach import Coach
from app.models.schemas.train import Train
from app.models.schemas.user import User


class TestTrainController:

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

        self.admin = User(
            id=2,
            name="Admin",
            user_name="admin@test.com",
            password="secret",
            role=Role.ADMIN,
        )

        self.app.dependency_overrides[get_train_service] = (
            lambda: self.service
        )

        self.app.dependency_overrides[get_current_user] = (
            lambda: self.user
        )

        self.app.dependency_overrides[get_current_admin] = (
            lambda: self.admin
        )

    def test_get_all_trains(self):
        train = Train(
            id=1,
            train_number="12345",
            train_name="Rajdhani Express",
            source="Delhi",
            destination="Mumbai",
            departure_time="10:00",
            arrival_time="18:00",
        )

        self.service.get_all_trains.return_value = [train]

        response = self.client.get("/trains")

        assert response.status_code == 200

        body = response.json()

        assert body["success"] is True
        assert body["message"] == "Trains fetched successfully"

        assert body["data"] == [
            {
                "train_number": "12345",
                "train_name": "Rajdhani Express",
                "source": "Delhi",
                "destination": "Mumbai",
                "departure_time": "10:00",
                "arrival_time": "18:00",
            }
        ]

        self.service.get_all_trains.assert_awaited_once_with()

    def test_add_train(self):
        train = Train(
            id=1,
            train_number="12345",
            train_name="Rajdhani Express",
            source="Delhi",
            destination="Mumbai",
            departure_time="10:00",
            arrival_time="18:00",
        )

        self.service.add_train.return_value = train

        response = self.client.post(
            "/trains",
            json={
                "train_number": "12345",
                "train_name": "Rajdhani Express",
                "source": "Delhi",
                "destination": "Mumbai",
                "departure_time": "10:00",
                "arrival_time": "18:00",
            },
        )

        assert response.status_code == 201

        body = response.json()

        assert body["success"] is True
        assert body["message"] == "Train created successfully"

        assert body["data"] == {
            "train_number": "12345",
            "train_name": "Rajdhani Express",
            "source": "Delhi",
            "destination": "Mumbai",
            "departure_time": "10:00",
            "arrival_time": "18:00",
        }

        self.service.add_train.assert_awaited_once()

        args = self.service.add_train.await_args.args


    def test_get_seat_layout(self):
        coach = Coach(
            id=1,
            train_id=1,
            coach_number="S1",
            class_type=CoachClass.SLEEPER,
            total_seat_capacity=72,
            rac_capacity=6,
        )

        coach.seats = []

        self.service.get_layout.return_value = [coach]

        response = self.client.get(
            "/trains/1/layout",
            params={
                "journey_date": "2026-09-15",
                "class_type": "SL",
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["success"] is True
        assert body["message"] == "Seat layout retrieved successfully"

        assert body["data"] == [
            {
                "coach_id": 1,
                "coach_number": "S1",
                "class_type": "SL",
                "seats": [],
            }
        ]

        self.service.get_layout.assert_awaited_once_with(
            1,
            date(2026, 9, 15),
            CoachClass.SLEEPER,
        )