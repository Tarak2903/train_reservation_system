from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.TrainRepository import TrainRepository


@pytest.fixture
def db():
    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    return db


def scalar_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


@pytest.mark.asyncio
async def test_find_train_by_id_returns_train(db):
    train = MagicMock()
    db.execute.return_value = scalar_result(train)
    repo = TrainRepository(db)

    assert await repo.find_train_by_id(1) is train


@pytest.mark.asyncio
async def test_find_train_by_number_returns_train(db):
    train = MagicMock()
    db.execute.return_value = scalar_result(train)
    repo = TrainRepository(db)

    assert await repo.find_train_by_number("12345") is train


@pytest.mark.asyncio
async def test_add_train_adds_flushes_and_returns_train(db):
    train = MagicMock()
    repo = TrainRepository(db)

    assert await repo.add_train(train) is train
    db.add.assert_called_once_with(train)
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_coach_returns_coach(db):
    coach = MagicMock()
    db.execute.return_value = scalar_result(coach)
    repo = TrainRepository(db)

    assert await repo.find_coach(2) is coach


@pytest.mark.asyncio
async def test_find_all_train_on_journey_date_returns_trains(db):
    trains = [MagicMock(), MagicMock()]
    result = MagicMock()
    result.scalars.return_value.all.return_value = trains
    db.execute.return_value = result
    repo = TrainRepository(db)

    assert await repo.find_all_train_on_journey_date("2026-09-15") == trains


@pytest.mark.asyncio
async def test_get_all_trains_returns_trains(db):
    trains = [MagicMock(), MagicMock()]
    result = MagicMock()
    result.scalars.return_value.all.return_value = trains
    db.execute.return_value = result
    repo = TrainRepository(db)

    assert await repo.get_all_trains() == trains
