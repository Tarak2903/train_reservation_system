from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.booking_repository import BookingRepository
from app.models.schemas.train import Train


@pytest.fixture
def db():
    return AsyncMock()


@pytest.fixture
def repo(db):
    return BookingRepository(db)

#
# @pytest.mark.asyncio
# async def test_try_lock_seat(db, repo):
#     result = MagicMock()
#     result.scalar.return_value = True
#
#     db.execute.return_value = result
#
#     response = await repo.try_lock_seat("2026-09-20", 1)
#
#     assert response is True
#     db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_booking(db, repo):
    result = MagicMock()
    booking = MagicMock()

    result.scalar_one_or_none.return_value = booking
    db.execute.return_value = result

    response = await repo.find_booking(1)

    assert response == booking
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_user(db, repo):
    result = MagicMock()
    user = MagicMock()

    result.scalar_one_or_none.return_value = user
    db.execute.return_value = result

    response = await repo.find_user(1)

    assert response == user
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_schedule(db, repo):
    result = MagicMock()
    schedule = MagicMock()

    result.scalar_one_or_none.return_value = schedule
    db.execute.return_value = result

    response = await repo.find_schedule(1, "2026-09-20")

    assert response == schedule
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_booking(db, repo):
    booking = MagicMock()

    response = await repo.add_booking(booking)

    assert response == booking
    db.add.assert_called_once_with(booking)
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_passenger(db, repo):
    passenger = MagicMock()

    await repo.add_passenger(passenger)

    db.add.assert_called_once_with(passenger)


@pytest.mark.asyncio
async def test_find_active_passenger_on_journey(db, repo):
    result = MagicMock()
    passenger = MagicMock()

    result.scalar_one_or_none.return_value = passenger
    db.execute.return_value = result

    response = await repo.find_active_passenger_on_journey(
        1,
        2,
        "2026-09-20",
    )

    assert response == passenger
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_seats(db, repo):
    result = MagicMock()
    seats = [MagicMock(), MagicMock()]

    result.scalars.return_value.all.return_value = seats
    db.execute.return_value = result

    response = await repo.get_seats(1, "AC")

    assert response == seats
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_occupied_seat_ids(db, repo):
    result = MagicMock()

    result.all.return_value = [
        (1,),
        (2,),
        (3,),
    ]

    db.execute.return_value = result

    response = await repo.get_occupied_seat_ids(
        1,
        "2026-09-20",
        "AC",
    )

    assert response == {1, 2, 3}
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_active_queue(db, repo):
    result = MagicMock()
    passengers = [MagicMock(), MagicMock()]

    result.scalars.return_value.all.return_value = passengers
    db.execute.return_value = result

    response = await repo.get_active_queue(
        1,
        "2026-09-20",
        "AC",
        "CNF",
    )

    assert response == passengers
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_next_sequence(db, repo):
    result = MagicMock()
    result.scalar.return_value = 5

    db.execute.return_value = result

    response = await repo.get_next_sequence(
        1,
        "AC",
        "RAC",
    )

    assert response == 6
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_next_sequence_when_empty(db, repo):
    result = MagicMock()
    result.scalar.return_value = None

    db.execute.return_value = result

    response = await repo.get_next_sequence(
        1,
        "AC",
        "RAC",
    )

    assert response == 1


@pytest.mark.asyncio
async def test_get_queue_count(db, repo):
    result = MagicMock()
    result.scalar_one.return_value = 5

    db.execute.return_value = result

    response = await repo.get_queue_count(
        1,
        "AC",
        "RAC",
    )

    assert response == 5
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_confirmed_count(db, repo):
    result = MagicMock()
    result.scalar_one.return_value = 4

    db.execute.return_value = result

    response = await repo.get_confirmed_count(1, "AC")

    assert response == 4
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_total_seat_count(db, repo):
    result = MagicMock()
    result.scalar.return_value = 100

    db.execute.return_value = result

    response = await repo.get_total_seat_count(1, "AC")

    assert response == 100
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_total_seat_count_when_empty(db, repo):
    result = MagicMock()
    result.scalar.return_value = None

    db.execute.return_value = result

    response = await repo.get_total_seat_count(1, "AC")

    assert response == 0


@pytest.mark.asyncio
async def test_get_total_rac_capacity(db, repo):
    result = MagicMock()
    result.scalar.return_value = 20

    db.execute.return_value = result

    response = await repo.get_total_rac_capacity(1, "AC")

    assert response == 20
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_total_rac_capacity_when_empty(db, repo):
    result = MagicMock()
    result.scalar.return_value = None

    db.execute.return_value = result

    response = await repo.get_total_rac_capacity(1, "AC")

    assert response == 0


@pytest.mark.asyncio
async def test_find_top_k_status_passengers(db, repo):
    result = MagicMock()
    passengers = [MagicMock(), MagicMock()]

    result.scalars.return_value.all.return_value = passengers
    db.execute.return_value = result

    booking = MagicMock()
    booking.train_id = 1
    booking.schedule_id = 2
    booking.class_type = "AC"

    response = await repo.find_top_k_status_passengers(
        booking,
        2,
        "RAC",
    )

    assert response == passengers
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_commit(db, repo):
    await repo.commit()

    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh(db, repo):
    obj = MagicMock()

    await repo.refresh(obj)

    db.refresh.assert_awaited_once_with(obj)


@pytest.mark.asyncio
async def test_rollback(db, repo):
    await repo.rollback()

    db.rollback.assert_awaited_once()