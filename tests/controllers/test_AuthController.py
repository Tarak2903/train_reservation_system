from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.controller.AuthController import router
from app.dependency import get_auth_service
from app.models.enums import Role
from app.models.schemas.user import User


class TestAuthController:

    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(router)

        self.client = TestClient(self.app)
        self.service = AsyncMock()

        self.app.dependency_overrides[get_auth_service] = (
            lambda: self.service
        )

    def test_signup_user(self):
        user = User(
            id=1,
            name="Tarak",
            user_name="tarakkhurana29@gmail.com",
            password="Tarak@29",
            role=Role.USER,
        )

        self.service.signup_user.return_value = user

        response = self.client.post(
            "/auth/signup",
            json={
                "name": "Tarak",
                "user_name": "tarakkhurana29@gmail.com",
                "password": "Tarak@29",
            },
        )

        assert response.status_code == 201

        body = response.json()

        assert body["success"] is True
        assert body["message"] == "User created successfully"
        assert body["data"] == {
            "user_id": 1,
            "user_name": "tarakkhurana29@gmail.com",
            "role": "USER",
        }

        self.service.signup_user.assert_awaited_once()


    def test_login_user(self):
        self.service.login_user.return_value = "access-token"

        response = self.client.post(
            "/auth/login",
            data={
                "username": "tarakkhurana29@gmail.com",
                "password": "Tarak@29",
            },
        )

        assert response.status_code == 200

        assert response.json() == {
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": "access-token",
                "token_type": "bearer",
            },
            'errors':[]
        }

        self.service.login_user.assert_awaited_once()



