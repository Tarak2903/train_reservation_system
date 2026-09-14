from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions.ResourceNotFoundException import ResourceNotFoundException
from app.exceptions.ResrouceAlreadyExistsException import ResourceAlreadyExistsException
from app.exceptions.train_exceptions import TrainNotFoundException
from app.models.enums import CoachClass
from app.services.CoachService import CoachService


@pytest.fixture
def repos():
    return AsyncMock(), AsyncMock(), AsyncMock()


@pytest.fixture
def service(repos):
    coach_repo, train_repo, seat_repo = repos
    return CoachService(coach_repo, train_repo, seat_repo)


@pytest.mark.asyncio
async def test_validate_train_by_id_raises_when_missing(service, repos):
    _, train_repo, _ = repos
    train_repo.find_train_by_id.return_value = None

    with pytest.raises(ResourceNotFoundException):
        await service.validate_train_by_id(1)


@pytest.mark.asyncio
async def test_validate_train_by_id_returns_train(service, repos):
    _, train_repo, _ = repos
    train = MagicMock()
    train_repo.find_train_by_id.return_value = train

    result = await service.validate_train_by_id(1)

    assert result is train


@pytest.mark.asyncio
async def test_validate_train_by_number_raises_when_missing(service, repos):
    _, train_repo, _ = repos
    train_repo.find_train_by_number.return_value = None

    with pytest.raises(TrainNotFoundException):
        await service.validate_train_by_number("12345")


@pytest.mark.asyncio
async def test_validate_train_by_number_succeeds_when_found(service, repos):
    _, train_repo, _ = repos
    train_repo.find_train_by_number.return_value = MagicMock()

    result = await service.validate_train_by_number("12345")

    assert result is None


@pytest.mark.asyncio
async def test_add_coach_successfully_creates_coach_and_seats(service, repos):
    coach_repo, train_repo, seat_repo = repos
    train_repo.find_train_by_id.return_value = MagicMock()
    coach_repo.find_coach_by_coach_number_and_train_id.return_value = None
    train_repo.db = AsyncMock()

    request = MagicMock(
        coach_number="S1",
        class_type=CoachClass.SLEEPER,
        total_seat_capacity=3,
        rac_capacity=2,
    )

    async def add_coach(coach):
        coach.id = 10
        return coach

    coach_repo.add_coach.side_effect = add_coach

    result = await service.add_coach(1, request)

    assert result.id == 10
    assert result.train_id == 1
    assert result.coach_number == "S1"
    assert result.total_seat_capacity == 3
    assert result.rac_capacity == 2
    seat_repo.add_seat.assert_awaited_once()
    train_repo.db.commit.assert_awaited_once()
    train_repo.db.refresh.assert_awaited_once_with(result)

    seats = seat_repo.add_seat.await_args.args[0]
    assert [seat.seat_number for seat in seats] == [1, 2, 3]
    assert all(seat.coach_id == 10 for seat in seats)


@pytest.mark.asyncio
async def test_add_coach_raises_when_coach_already_exists(service, repos):
    coach_repo, train_repo, _ = repos
    train_repo.find_train_by_id.return_value = MagicMock()
    coach_repo.find_coach_by_coach_number_and_train_id.return_value = MagicMock()
    request = MagicMock(coach_number="S1")

    with pytest.raises(ResourceAlreadyExistsException):
        await service.add_coach(1, request)

    coach_repo.add_coach.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_seat_raises_when_coach_missing(service, repos):
    _, train_repo, seat_repo = repos
    train_repo.find_coach.return_value = None

    with pytest.raises(ResourceNotFoundException):
        await service.add_seat(10, 3)

    seat_repo.add_seat.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_seat_creates_sequential_seats(service, repos):
    _, train_repo, seat_repo = repos
    train_repo.find_coach.return_value = MagicMock()

    result = await service.add_seat(10, 4)

    assert len(result) == 4
    assert [seat.seat_number for seat in result] == [1, 2, 3, 4]
    assert all(seat.coach_id == 10 for seat in result)
    seat_repo.add_seat.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_get_coaches_by_train_number_returns_coaches(service, repos):
    coach_repo, train_repo, _ = repos
    train_repo.find_train_by_number.return_value = MagicMock()
    response = MagicMock()
    response.coaches = [MagicMock(), MagicMock()]
    coach_repo.get_coaches_by_train_number.return_value = response

    result = await service.get_coaches_by_train_number("12345")

    assert result == response.coaches
    coach_repo.get_coaches_by_train_number.assert_awaited_once_with("12345")


@pytest.mark.asyncio
async def test_get_coaches_by_train_number_raises_when_no_coaches(service, repos):
    coach_repo, train_repo, _ = repos
    train_repo.find_train_by_number.return_value = MagicMock()
    coach_repo.get_coaches_by_train_number.return_value = None

    with pytest.raises(ResourceNotFoundException):
        await service.get_coaches_by_train_number("12345")
