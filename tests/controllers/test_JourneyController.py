from datetime import date
from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth import get_current_admin
from app.controller.JourneyController import router
from app.dependency import get_journey_service
from app.models.enums import Role
from app.models.schemas.train_schedule import TrainSchedule
from app.models.schemas.user import User


class TestJourneyController:

    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(router)

        self.client = TestClient(self.app)
        self.service = AsyncMock()

        self.admin = User(
            id=1,
            name="Admin",
            user_name="admin@test.com",
            password="secret",
            role=Role.ADMIN,
        )

        self.app.dependency_overrides[get_journey_service] = (
            lambda: self.service
        )

        self.app.dependency_overrides[get_current_admin] = (
            lambda: self.admin
        )

    def test_add_train_journey(self):
        journey = TrainSchedule(
            id=1,
            train_id=10,
            journey_date=date(2026, 9, 15),
        )

        self.service.add_journey.return_value = journey

        response = self.client.post(
            "/trains/10/journeys",
            json={
                "journey_date": "2026-09-15",
            },
        )

        assert response.status_code == 201

        body = response.json()

        assert body["success"] is True
        assert body["message"] == "Train journey added successfully"

        assert body["data"] == {
            "journey_id": 1,
            "train_id": 10,
            "journey_date": "2026-09-15",
        }

        self.service.add_journey.assert_awaited_once()

        args = self.service.add_journey.await_args.args

        assert args[0] == 10
        assert args[1].journey_date == date(2026, 9, 15)