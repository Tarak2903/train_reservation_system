from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.BookingRepository import BookingRepository
from app.models.enums import BookingStatus, CoachClass, PassengerStatus


@pytest.fixture
def db():
    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()
    return db


def scalars_result(values):
    result = MagicMock()
    result.scalars.return_value.all.return_value = values
    return result


def scalar_one_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


@pytest.mark.asyncio
async def test_find_booking_returns_booking(db):
    booking = MagicMock()
    db.execute.return_value = scalar_one_result(booking)
    repo = BookingRepository(db)

    assert await repo.find_booking(1) is booking


@pytest.mark.asyncio
async def test_find_user_returns_user(db):
    user = MagicMock()
    db.execute.return_value = scalar_one_result(user)
    repo = BookingRepository(db)

    assert await repo.find_user(1) is user


@pytest.mark.asyncio
async def test_find_schedule_returns_schedule(db):
    schedule = MagicMock()
    db.execute.return_value = scalar_one_result(schedule)
    repo = BookingRepository(db)

    assert await repo.find_schedule(1, "2026-09-15") is schedule


@pytest.mark.asyncio
async def test_add_booking_adds_and_flushes(db):
    booking = MagicMock()
    repo = BookingRepository(db)

    assert await repo.add_booking(booking) is booking
    db.add.assert_called_once_with(booking)
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_passenger_adds_passenger(db):
    passenger = MagicMock()
    repo = BookingRepository(db)

    result = await repo.add_passenger(passenger)

    assert result is None
    db.add.assert_called_once_with(passenger)


@pytest.mark.asyncio
async def test_find_active_passenger_on_journey_returns_passenger(db):
    passenger = MagicMock()
    db.execute.return_value = scalar_one_result(passenger)
    repo = BookingRepository(db)

    assert await repo.find_active_passenger_on_journey(1, 2, "2026-09-15") is passenger


@pytest.mark.asyncio
async def test_get_seats_returns_seats(db):
    seats = [MagicMock(), MagicMock()]
    db.execute.return_value = scalars_result(seats)
    repo = BookingRepository(db)

    assert await repo.get_seats(1, CoachClass.SLEEPER) == seats


@pytest.mark.asyncio
async def test_get_occupied_seat_ids_returns_set(db):
    result = MagicMock()
    result.all.return_value = [(1,), (3,)]
    db.execute.return_value = result
    repo = BookingRepository(db)

    assert await repo.get_occupied_seat_ids(1, "2026-09-15", CoachClass.SLEEPER) == {1, 3}


@pytest.mark.asyncio
async def test_get_active_queue_returns_passengers(db):
    passengers = [MagicMock(), MagicMock()]
    db.execute.return_value = scalars_result(passengers)
    repo = BookingRepository(db)

    assert await repo.get_active_queue(1, "2026-09-15", CoachClass.SLEEPER, PassengerStatus.RAC) == passengers


@pytest.mark.asyncio
async def test_get_next_sequence_returns_one_when_no_previous_sequence(db):
    result = MagicMock()
    result.scalar.return_value = None
    db.execute.return_value = result
    repo = BookingRepository(db)

    assert await repo.get_next_sequence(1, CoachClass.SLEEPER, PassengerStatus.RAC) == 1


@pytest.mark.asyncio
async def test_get_next_sequence_increments_previous_sequence(db):
    result = MagicMock()
    result.scalar.return_value = 7
    db.execute.return_value = result
    repo = BookingRepository(db)

    assert await repo.get_next_sequence(1, CoachClass.SLEEPER, PassengerStatus.RAC) == 8


@pytest.mark.asyncio
async def test_get_queue_count_returns_count(db):
    result = MagicMock()
    result.scalar_one.return_value = 4
    db.execute.return_value = result
    repo = BookingRepository(db)

    assert await repo.get_queue_count(1, CoachClass.SLEEPER, PassengerStatus.RAC) == 4


@pytest.mark.asyncio
async def test_get_confirmed_count_returns_count(db):
    result = MagicMock()
    result.scalar_one.return_value = 6
    db.execute.return_value = result
    repo = BookingRepository(db)

    assert await repo.get_confirmed_count(1, CoachClass.SLEEPER) == 6


@pytest.mark.asyncio
async def test_get_total_seat_count_returns_sum_or_zero(db):
    result = MagicMock()
    result.scalar.return_value = 20
    db.execute.return_value = result
    repo = BookingRepository(db)

    assert await repo.get_total_seat_count(1, CoachClass.SLEEPER) == 20


@pytest.mark.asyncio
async def test_get_total_seat_count_returns_zero_for_none(db):
    result = MagicMock()
    result.scalar.return_value = None
    db.execute.return_value = result
    repo = BookingRepository(db)

    assert await repo.get_total_seat_count(1, CoachClass.SLEEPER) == 0


@pytest.mark.asyncio
async def test_get_total_rac_capacity_returns_sum_or_zero(db):
    result = MagicMock()
    result.scalar.return_value = 5
    db.execute.return_value = result
    repo = BookingRepository(db)

    assert await repo.get_total_rac_capacity(1, CoachClass.SLEEPER) == 5


@pytest.mark.asyncio
async def test_find_top_k_status_passengers_returns_passengers(db):
    passengers = [MagicMock()]
    db.execute.return_value = scalars_result(passengers)
    repo = BookingRepository(db)
    booking = MagicMock(train_id=1, schedule_id=2, class_type=CoachClass.SLEEPER)

    assert await repo.find_top_k_status_passengers(booking, 1, PassengerStatus.WL) == passengers


@pytest.mark.asyncio
async def test_commit_refresh_and_rollback_delegate_to_db(db):
    repo = BookingRepository(db)
    obj = MagicMock()

    await repo.commit()
    await repo.refresh(obj)
    await repo.rollback()

    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(obj)
    db.rollback.assert_awaited_once()
