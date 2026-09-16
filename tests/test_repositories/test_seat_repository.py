from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.seat_repository import SeatRepository


@pytest.fixture
def db():
    return AsyncMock()


@pytest.fixture
def repo(db):
    return SeatRepository(db)


@pytest.mark.asyncio
async def test_add_seat(db, repo):
    seats = [MagicMock(), MagicMock()]

    response = await repo.add_seat(seats)

    assert response == seats
    db.add_all.assert_called_once_with(seats)
    db.flush.assert_awaited_once()