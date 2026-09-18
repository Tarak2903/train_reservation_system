from datetime import datetime, timezone, timedelta

import jwt
from pwdlib import PasswordHash

from app.helpers.config import settings
from app.models.enums import Role
from app.exceptions.unauthenticated_exception import UnauthenticatedException
from app.exceptions.user_exceptions import (
    ResourceAlreadyExistsException,
    ResourceNotFoundException
)
from app.models.schemas.user import User


class AuthService:
    def __init__(self, auth_repo):
        self.auth_repo = auth_repo
        self.password_hash = PasswordHash.recommended()

    @staticmethod
    def create_token(payload: dict):
        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )


    async def signup_user(self, user_request):
        if await self.auth_repo.find_user_by_username(user_request.user_name):
            raise ResourceAlreadyExistsException("User already exists")

        user = User(
            name=user_request.name,
            user_name=user_request.user_name,
            password=self.password_hash.hash(user_request.password),
            role=Role.USER,
        )
        return await self.auth_repo.add_user(user)


    async def login_user(self, user):
        user_info = await self.auth_repo.find_user_by_username(user.username)

        if user_info is None:
            raise ResourceNotFoundException("User doesnt exists")

        if not self.password_hash.verify(user.password, user_info.password):
            raise UnauthenticatedException("User not authorized")

        return self.create_token(
            {
                "user_name": user.username,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            }
        )
