from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions.train_exceptions import TrainAlreadyExistsException, TrainNotFoundException
from app.models.enums import CoachClass
from app.services.TrainService import TrainService


@pytest.fixture
def repos():
    return AsyncMock(), AsyncMock(), AsyncMock()


@pytest.fixture
def service(repos):
    train_repo, journey_repo, coach_repo = repos
    return TrainService(train_repo, journey_repo, coach_repo)


@pytest.mark.asyncio
async def test_check_existing_train_by_number_raises_when_train_exists(service, repos):
    train_repo, _, _ = repos
    train_repo.find_train_by_number.return_value = MagicMock()
    request = MagicMock(train_number="12345")

    with pytest.raises(TrainAlreadyExistsException):
        await service.check_existing_train_by_number(request)

    train_repo.find_train_by_number.assert_awaited_once_with("12345")


@pytest.mark.asyncio
async def test_check_existing_train_by_number_does_nothing_when_train_missing(service, repos):
    train_repo, _, _ = repos
    train_repo.find_train_by_number.return_value = None
    request = MagicMock(train_number="12345")

    await service.check_existing_train_by_number(request)

    train_repo.find_train_by_number.assert_awaited_once_with("12345")


@pytest.mark.asyncio
async def test_add_train_creates_train_and_seven_schedules(service, repos):
    train_repo, journey_repo, _ = repos
    train_repo.find_train_by_number.return_value = None
    train_repo.add_train.side_effect = lambda train: setattr(train, "id", 1)
    train_repo.db = AsyncMock()

    request = MagicMock()
    request.model_dump.return_value = {
        "train_number": "12345",
        "train_name": "Express",
        "source": "Delhi",
        "destination": "Mumbai",
        "departure_time": "10:00",
        "arrival_time": "20:00",
    }

    with patch("app.services.TrainService.date") as mocked_date:
        mocked_date.today.return_value = date(2026, 9, 13)
        result = await service.add_train(request)

    assert result.train_number == "12345"
    assert result.id == 1
    assert journey_repo.add_schedule.await_count == 7
    train_repo.db.commit.assert_awaited_once()
    train_repo.db.refresh.assert_awaited_once_with(result)

    dates = [call.args[0].journey_date for call in journey_repo.add_schedule.await_args_list]
    assert dates == [date(2026, 9, 13 + i) for i in range(7)]


@pytest.mark.asyncio
async def test_add_train_does_not_create_when_train_exists(service, repos):
    train_repo, journey_repo, _ = repos
    train_repo.find_train_by_number.return_value = MagicMock()
    request = MagicMock(train_number="12345")

    with pytest.raises(TrainAlreadyExistsException):
        await service.add_train(request)

    train_repo.add_train.assert_not_awaited()
    journey_repo.add_schedule.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_layout_raises_when_train_missing(service, repos):
    train_repo, journey_repo, coach_repo = repos
    train_repo.find_train_by_id.return_value = None

    with pytest.raises(TrainNotFoundException):
        await service.get_layout(1, date(2026, 9, 15), CoachClass.SLEEPER)

    train_repo.find_train_by_id.assert_awaited_once_with(1)
    journey_repo.find_schedule.assert_not_awaited()
    coach_repo.get_coaches_by_train_id_and_class_type.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_layout_raises_when_journey_missing(service, repos):
    train_repo, journey_repo, coach_repo = repos
    train_repo.find_train_by_id.return_value = MagicMock()
    journey_repo.find_schedule.return_value = None

    with pytest.raises(TrainNotFoundException):
        await service.get_layout(1, date(2026, 9, 15), CoachClass.SLEEPER)

    journey_repo.find_schedule.assert_awaited_once_with(1, date(2026, 9, 15))
    coach_repo.get_coaches_by_train_id_and_class_type.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_layout_returns_coaches(service, repos):
    train_repo, journey_repo, coach_repo = repos
    train_repo.find_train_by_id.return_value = MagicMock()
    journey_repo.find_schedule.return_value = MagicMock()
    coaches = [MagicMock(), MagicMock()]
    coach_repo.get_coaches_by_train_id_and_class_type.return_value = coaches

    result = await service.get_layout(1, date(2026, 9, 15), CoachClass.SLEEPER)

    assert result == coaches
    coach_repo.get_coaches_by_train_id_and_class_type.assert_awaited_once_with(
        1, CoachClass.SLEEPER
    )


@pytest.mark.asyncio
async def test_get_all_trains_returns_trains(service, repos):
    train_repo, _, _ = repos
    trains = [MagicMock(), MagicMock()]
    train_repo.get_all_trains.return_value = trains

    result = await service.get_all_trains()

    assert result == trains
    train_repo.get_all_trains.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_trains_raises_when_empty(service, repos):
    train_repo, _, _ = repos
    train_repo.get_all_trains.return_value = []

    with pytest.raises(TrainNotFoundException):
        await service.get_all_trains()


@pytest.mark.asyncio
async def test_find_train_by_number_returns_repository_result(service, repos):
    train_repo, _, _ = repos
    train = MagicMock()
    train_repo.find_train_by_number.return_value = train

    result = await service.find_train_by_number("12345")

    assert result is train
    train_repo.find_train_by_number.assert_awaited_once_with("12345")
