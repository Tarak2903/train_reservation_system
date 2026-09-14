from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.SeatRepository import SeatRepository


@pytest.mark.asyncio
async def test_add_seat_adds_flushes_and_returns_seats():
    db = MagicMock()
    db.flush = AsyncMock()
    seats = [MagicMock(), MagicMock()]
    repo = SeatRepository(db)

    result = await repo.add_seat(seats)

    db.add_all.assert_called_once_with(seats)
    db.flush.assert_awaited_once()
    assert result is seats
