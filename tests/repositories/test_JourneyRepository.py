from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.JourneyRepository import JourneyRepository


@pytest.fixture
def db():
    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    return db


def result_with_scalar(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


@pytest.mark.asyncio
async def test_add_schedule_adds_flushes_and_returns_schedule(db):
    schedule = MagicMock()
    repo = JourneyRepository(db)

    result = await repo.add_schedule(schedule)

    db.add.assert_called_once_with(schedule)
    db.flush.assert_awaited_once()
    assert result is schedule


@pytest.mark.asyncio
async def test_find_schedule_returns_schedule(db):
    schedule = MagicMock()
    db.execute.return_value = result_with_scalar(schedule)
    repo = JourneyRepository(db)

    assert await repo.find_schedule(1, "2026-09-15") is schedule
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_schedule_returns_none(db):
    db.execute.return_value = result_with_scalar(None)
    repo = JourneyRepository(db)

    assert await repo.find_schedule(1, "2026-09-15") is None


@pytest.mark.asyncio
async def test_find_journey_date_returns_schedule(db):
    schedule = MagicMock()
    db.execute.return_value = result_with_scalar(schedule)
    repo = JourneyRepository(db)

    assert await repo.find_journey_date("2026-09-15") is schedule
