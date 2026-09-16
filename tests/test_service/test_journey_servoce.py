from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.train_service import TrainService


@pytest.fixture
def repos():
    return AsyncMock(), AsyncMock(), AsyncMock()


@pytest.fixture
def service(repos):
    train_repo, journey_repo, coach_repo = repos
    return TrainService(
        train_repo,
        journey_repo,
        coach_repo
    )


@pytest.mark.asyncio
async def test_check_existing_train_by_number(repos, service):
    train_repo, journey_repo, coach_repo = repos

    request = MagicMock()
    request.train_number = "12345"

    train_repo.find_train_by_number.return_value = None

    response = await service.check_existing_train_by_number(request)

    assert response is None

    train_repo.find_train_by_number.assert_awaited_once_with(
        "12345"
    )


@pytest.mark.asyncio
async def test_get_all_trains(repos, service):
    train_repo, journey_repo, coach_repo = repos

    trains = [MagicMock(), MagicMock()]

    train_repo.get_all_trains.return_value = trains

    response = await service.get_all_trains(None)

    assert response == trains

    train_repo.get_all_trains.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_train_by_number(repos, service):
    train_repo, journey_repo, coach_repo = repos

    trains = [MagicMock()]

    train_repo.find_train_by_number.return_value = trains

    response = await service.find_train_by_number("12345")

    assert response == trains

    train_repo.find_train_by_number.assert_awaited_once_with(
        "12345"
    )


@pytest.mark.asyncio
async def test_get_layout(repos, service):
    train_repo, journey_repo, coach_repo = repos

    train = MagicMock()
    schedule = MagicMock()
    coaches = [MagicMock()]

    train_repo.find_train_by_id.return_value = train
    journey_repo.find_schedule.return_value = schedule
    coach_repo.get_coaches_by_train_id_and_class_type.return_value = coaches

    response = await service.get_layout(
        10,
        "2026-09-20",
        "SL"
    )

    assert response == coaches

    train_repo.find_train_by_id.assert_awaited_once_with(10)
    journey_repo.find_schedule.assert_awaited_once_with(
        10,
        "2026-09-20"
    )
    coach_repo.get_coaches_by_train_id_and_class_type.assert_awaited_once_with(
        10,
        "SL"
    )


@pytest.mark.asyncio
async def test_update_train(repos, service):
    train_repo, journey_repo, coach_repo = repos

    train = MagicMock()

    request = MagicMock()
    request.model_dump.return_value = {
        "train_name": "Updated Train"
    }

    train_repo.find_train_by_id.return_value = train
    train_repo.db = AsyncMock()

    response = await service.update_train(10, request)

    assert response == train
    assert train.train_name == "Updated Train"

    train_repo.find_train_by_id.assert_awaited_once_with(10)
    train_repo.db.commit.assert_awaited_once()
    train_repo.db.refresh.assert_awaited_once_with(train)

