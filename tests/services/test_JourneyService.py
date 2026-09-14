from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions.ResourceNotFoundException import ResourceNotFoundException
from app.exceptions.ResrouceAlreadyExistsException import ResourceAlreadyExistsException
from app.services.JourneyService import JourneyService


@pytest.fixture
def repos():
    return AsyncMock(), AsyncMock()


@pytest.fixture
def service(repos):
    journey_repo, train_repo = repos
    return JourneyService(journey_repo, train_repo)


@pytest.mark.asyncio
async def test_validate_train_by_id_raises_when_missing(service, repos):
    _, train_repo = repos
    train_repo.find_train_by_id.return_value = None

    with pytest.raises(ResourceNotFoundException):
        await service.validate_train_by_id(1)

    train_repo.find_train_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_validate_train_by_id_succeeds_when_found(service, repos):
    _, train_repo = repos
    train = MagicMock()
    train_repo.find_train_by_id.return_value = train

    result = await service.validate_train_by_id(1)

    assert result is None


@pytest.mark.asyncio
async def test_validate_journey_date_raises_when_date_exists(service, repos):
    journey_repo, _ = repos
    journey_repo.find_schedule.return_value = MagicMock()
    request = MagicMock(journey_date=date(2026, 9, 15))

    with pytest.raises(ResourceAlreadyExistsException):
        await service.validate_journey_date(1, request)

    journey_repo.find_schedule.assert_awaited_once_with(1, date(2026, 9, 15))


@pytest.mark.asyncio
async def test_validate_journey_date_succeeds_when_date_missing(service, repos):
    journey_repo, _ = repos
    journey_repo.find_schedule.return_value = None
    request = MagicMock(journey_date=date(2026, 9, 15))

    result = await service.validate_journey_date(1, request)

    assert result is None


@pytest.mark.asyncio
async def test_add_journey_creates_and_returns_schedule(service, repos):
    journey_repo, train_repo = repos
    train_repo.find_train_by_id.return_value = MagicMock()
    journey_repo.find_schedule.return_value = None
    journey_repo.db = AsyncMock()
    request = MagicMock(journey_date=date(2026, 9, 15))

    result = await service.add_journey(5, request)

    assert result.train_id == 5
    assert result.journey_date == date(2026, 9, 15)
    journey_repo.add_schedule.assert_awaited_once_with(result)
    journey_repo.db.commit.assert_awaited_once()
    journey_repo.db.refresh.assert_awaited_once_with(result)
