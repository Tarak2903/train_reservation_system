from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.AuthRepository import AuthRepository


@pytest.fixture
def db():
    db = MagicMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_find_user_by_username_returns_user(db):
    user = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    db.execute.return_value = result
    repo = AuthRepository(db)

    assert await repo.find_user_by_username("a@example.com") is user
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_user_by_username_returns_none(db):
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    repo = AuthRepository(db)

    assert await repo.find_user_by_username("a@example.com") is None


@pytest.mark.asyncio
async def test_add_user_adds_commits_refreshes_and_returns_user(db):
    user = MagicMock()
    repo = AuthRepository(db)

    result = await repo.add_user(user)

    db.add.assert_called_once_with(user)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(user)
    assert result is user
