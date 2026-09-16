from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.auth_repository import AuthRepository


@pytest.fixture
def db():
    return AsyncMock()


@pytest.fixture
def repo(db):
    return AuthRepository(db)


@pytest.mark.asyncio
async def test_find_user_by_username(db, repo):
    result = MagicMock()
    user = MagicMock()

    result.scalar_one_or_none.return_value = user
    db.execute.return_value = result

    response = await repo.find_user_by_username("tarak")

    assert response == user
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_user(db, repo):
    user = MagicMock()

    response = await repo.add_user(user)

    assert response == user
    db.add.assert_called_once_with(user)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(user)