from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth import get_current_admin
from app.controller.CoachController import router
from app.dependency import get_coach_service
from app.models.enums import CoachClass, Role
from app.models.schemas.coach import Coach
from app.models.schemas.user import User


class TestCoachController:

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

        self.app.dependency_overrides[get_coach_service] = (
            lambda: self.service
        )

        self.app.dependency_overrides[get_current_admin] = (
            lambda: self.admin
        )

    def test_get_coaches_by_train_number(self):
        coach = Coach(
            id=1,
            train_id=10,
            coach_number="S1",
            class_type=CoachClass.SLEEPER,
            total_seat_capacity=72,
            rac_capacity=6,
        )

        self.service.get_coaches_by_train_number.return_value = [coach]

        response = self.client.get(
            "/trains/train_number",
            params={"train_number": "12345"},
        )

        assert response.status_code == 200

        body = response.json()

        assert body["success"] is True
        assert body["message"] == "Coaches fetched successfully"

        assert body["data"] == [
            {
                "coach_number": "S1",
                "class_type": "SL",
                "total_seat_capacity": 72,
                "rac_capacity": 6,
            }
        ]

        self.service.get_coaches_by_train_number.assert_awaited_once_with(
            "12345"
        )

    def test_add_train_coach(self):
        coach = Coach(
            id=1,
            train_id=10,
            coach_number="S1",
            class_type=CoachClass.SLEEPER,
            total_seat_capacity=72,
            rac_capacity=6,
        )

        self.service.add_coach.return_value = coach

        response = self.client.post(
            "/trains/10/coaches",
            json={
                "coach_number": "S1",
                "class_type": "SL",
                "total_seat_capacity": 72,
                "rac_capacity": 6,
            },
        )

        assert response.status_code == 201

        body = response.json()

        assert body["success"] is True
        assert body["message"] == "Coach added successfully"

        assert body["data"] == {
            "coach_number": "S1",
            "class_type": "SL",
            "total_seat_capacity": 72,
            "rac_capacity": 6,
        }

        self.service.add_coach.assert_awaited_once()

        args = self.service.add_coach.await_args.args

        assert args[0] == 10
        assert args[1].coach_number == "S1"
        assert args[1].class_type == CoachClass.SLEEPER