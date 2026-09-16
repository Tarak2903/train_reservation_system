import pytest
from unittest.mock import AsyncMock, MagicMock
from app.models.schemas.booking import Booking,BookingPassenger
from app.models.schemas.user import User
from app.services.train_service import TrainService
from app.exceptions.train_exceptions import (
    ResourceNotFoundException,
    TrainAlreadyExistsException,
    TrainNotFoundException,
)


@pytest.fixture
def repos():
    return AsyncMock(), AsyncMock(), AsyncMock()


@pytest.fixture
def service(repos):
    train_repo, journey_repo, coach_repo = repos
    return TrainService(train_repo, journey_repo, coach_repo)


@pytest.mark.asyncio
async def test_check_existing_train_by_number(repos, service):
    train_repo, journey_repo, coach_repo = repos

    request = MagicMock()
    request.train_number = "12345"

    train_repo.find_train_by_number.return_value = None

    result = await service.check_existing_train_by_number(request)

    assert result is None


@pytest.mark.asyncio
async def test_check_existing_train_by_number_exists(repos, service):
    train_repo, journey_repo, coach_repo = repos

    request = MagicMock()
    request.train_number = "12345"

    train_repo.find_train_by_number.return_value = MagicMock()

    with pytest.raises(TrainAlreadyExistsException):
        await service.check_existing_train_by_number(request)


@pytest.mark.asyncio
async def test_add_train(repos, service):
    train_repo, journey_repo, coach_repo = repos

    request = MagicMock()
    request.train_number = "12345"
    request.model_dump.return_value = {
        "train_number": "12345",
        "train_name": "Test Express",
    }

    train_repo.find_train_by_number.return_value = None
    train_repo.db = AsyncMock()

    result = await service.add_train(request)

    assert result is not None

    train_repo.add_train.assert_awaited_once()
    assert journey_repo.add_schedule.await_count == 7
    train_repo.db.commit.assert_awaited_once()
    train_repo.db.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_train_already_exists(repos, service):
    train_repo, journey_repo, coach_repo = repos

    request = MagicMock()
    request.train_number = "12345"

    train_repo.find_train_by_number.return_value = MagicMock()

    with pytest.raises(TrainAlreadyExistsException):
        await service.add_train(request)


@pytest.mark.asyncio
async def test_get_layout(repos, service):
    train_repo, journey_repo, coach_repo = repos

    train_repo.find_train_by_id.return_value = MagicMock()
    journey_repo.find_schedule.return_value = MagicMock()
    coach_repo.get_coaches_by_train_id_and_class_type.return_value = []

    result = await service.get_layout(
        10,
        "2026-09-20",
        "SL"
    )

    assert result == []


@pytest.mark.asyncio
async def test_get_layout_train_not_found(repos, service):
    train_repo, journey_repo, coach_repo = repos

    train_repo.find_train_by_id.return_value = None

    with pytest.raises(TrainNotFoundException):
        await service.get_layout(
            10,
            "2026-09-20",
            "SL"
        )


@pytest.mark.asyncio
async def test_get_layout_journey_not_found(repos, service):
    train_repo, journey_repo, coach_repo = repos

    train_repo.find_train_by_id.return_value = MagicMock()
    journey_repo.find_schedule.return_value = None

    with pytest.raises(TrainNotFoundException):
        await service.get_layout(
            10,
            "2026-09-20",
            "SL"
        )


@pytest.mark.asyncio
async def test_get_all_trains_without_date(repos, service):
    train_repo, journey_repo, coach_repo = repos

    trains = [MagicMock(), MagicMock()]
    train_repo.get_all_trains.return_value = trains

    result = await service.get_all_trains(None)

    assert result == trains


@pytest.mark.asyncio
async def test_get_all_trains_without_date_not_found(repos, service):
    train_repo, journey_repo, coach_repo = repos

    train_repo.get_all_trains.return_value = []

    with pytest.raises(TrainNotFoundException):
        await service.get_all_trains(None)


@pytest.mark.asyncio
async def test_get_all_trains_on_date(repos, service):
    train_repo, journey_repo, coach_repo = repos

    trains = [MagicMock()]
    train_repo.find_all_train_on_journey_date.return_value = trains

    result = await service.get_all_trains("2026-09-20")

    assert result == trains


@pytest.mark.asyncio
async def test_get_all_trains_on_date_not_found(repos, service):
    train_repo, journey_repo, coach_repo = repos

    train_repo.find_all_train_on_journey_date.return_value = []

    with pytest.raises(TrainNotFoundException):
        await service.get_all_trains("2026-09-20")


@pytest.mark.asyncio
async def test_find_train_by_number(repos, service):
    train_repo, journey_repo, coach_repo = repos

    trains = [MagicMock()]
    train_repo.find_train_by_number.return_value = trains

    result = await service.find_train_by_number("12345")

    assert result == trains


@pytest.mark.asyncio
async def test_update_train(repos, service):
    train_repo, journey_repo, coach_repo = repos

    train = MagicMock()
    train_repo.find_train_by_id.return_value = train

    request = MagicMock()
    request.model_dump.return_value = {
        "train_name": "Updated Train"
    }

    result = await service.update_train(10, request)

    assert result == train
    assert train.train_name == "Updated Train"

    train_repo.db.commit.assert_awaited_once()
    train_repo.db.refresh.assert_awaited_once_with(train)


@pytest.mark.asyncio
async def test_update_train_not_found(repos, service):
    train_repo, journey_repo, coach_repo = repos

    train_repo.find_train_by_id.return_value = None

    request = MagicMock()

    with pytest.raises(ResourceNotFoundException):
        await service.update_train(10, request)
