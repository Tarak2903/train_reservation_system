from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.CoachRepository import CoachRepository


@pytest.fixture
def db():
    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_find_coach_by_number_returns_coach(db):
    coach = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = coach
    db.execute.return_value = result
    repo = CoachRepository(db)

    assert await repo.find_coach_by_coach_number_and_train_id(1, "S1") is coach
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_coaches_by_train_number_returns_train_with_coaches(db):
    train = MagicMock()
    train.coaches = [MagicMock(), MagicMock()]
    result = MagicMock()
    result.scalar_one_or_none.return_value = train
    db.execute.return_value = result
    repo = CoachRepository(db)

    assert await repo.get_coaches_by_train_number("12345") is train


@pytest.mark.asyncio
async def test_get_coaches_by_train_id_and_class_type_returns_list(db):
    coaches = [MagicMock(), MagicMock()]
    result = MagicMock()
    result.scalars.return_value.all.return_value = coaches
    db.execute.return_value = result
    repo = CoachRepository(db)

    assert await repo.get_coaches_by_train_id_and_class_type(1, "SL") == coaches


@pytest.mark.asyncio
async def test_add_coach_adds_flushes_and_returns_coach(db):
    coach = MagicMock()
    repo = CoachRepository(db)

    assert await repo.add_coach(coach) is coach
    db.add.assert_called_once_with(coach)
    db.flush.assert_awaited_once()
