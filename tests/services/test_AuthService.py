from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions.UnauthenticatedException import UnauthenticatedException
from app.exceptions.user_exceptions import ResourceAlreadyExistsException, ResourceNotFoundException
from app.models.enums import Role
from app.models.schemas.user import User
from app.services.AuthService import AuthService


@pytest.fixture
def auth_repo():
    return AsyncMock()


@pytest.fixture
def service(auth_repo):
    return AuthService(auth_repo)


@pytest.mark.asyncio
async def test_signup_user_raises_when_username_exists(service, auth_repo):
    auth_repo.find_user_by_username.return_value = MagicMock()
    request = MagicMock(user_name="test@example.com")

    with pytest.raises(ResourceAlreadyExistsException):
        await service.signup_user(request)

    auth_repo.add_user.assert_not_awaited()


@pytest.mark.asyncio
async def test_signup_user_creates_user(service, auth_repo):
    auth_repo.find_user_by_username.return_value = None
    created = MagicMock()
    auth_repo.add_user.return_value = created
    request = MagicMock(
        name="Tarak",
        user_name="test@example.com",
        password="secret123",
    )

    result = await service.signup_user(request)

    assert result is created
    auth_repo.add_user.assert_awaited_once()
    user = auth_repo.add_user.await_args.args[0]
    assert isinstance(user, User)
    assert user.name == "Tarak"
    assert user.user_name == "test@example.com"
    assert user.password != "secret123"
    assert user.role is Role.USER


@pytest.mark.asyncio
async def test_login_user_raises_when_user_missing(service, auth_repo):
    auth_repo.find_user_by_username.return_value = None
    request = MagicMock(username="test@example.com")

    with pytest.raises(ResourceNotFoundException):
        await service.login_user(request)


@pytest.mark.asyncio
async def test_login_user_raises_when_password_is_wrong(service, auth_repo):
    stored_user = MagicMock(password="hashed-password")
    auth_repo.find_user_by_username.return_value = stored_user
    request = MagicMock(username="test@example.com", password="wrong")

    with patch.object(service.password_hash, "verify", return_value=False):
        with pytest.raises(UnauthenticatedException):
            await service.login_user(request)


@pytest.mark.asyncio
async def test_login_user_returns_token_when_credentials_are_valid(service, auth_repo):
    stored_user = MagicMock(password="hashed-password")
    auth_repo.find_user_by_username.return_value = stored_user
    request = MagicMock(username="test@example.com", password="correct")

    with patch.object(service.password_hash, "verify", return_value=True), \
         patch.object(service, "create_token", return_value="jwt-token") as create_token:
        result = await service.login_user(request)

    assert result == "jwt-token"
    create_token.assert_called_once()
    payload = create_token.call_args.args[0]
    assert payload["user_name"] == "test@example.com"
    assert isinstance(payload["exp"], datetime)


def test_create_token_returns_jwt():
    with patch("app.services.AuthService.jwt.encode", return_value="encoded-token") as encode:
        result = AuthService.create_token({"user_name": "test@example.com"})

    assert result == "encoded-token"
    encode.assert_called_once()
