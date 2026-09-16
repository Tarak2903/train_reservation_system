from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.train_repository import TrainRepository
from app.models.schemas.booking import Booking
from app.models.schemas.seat import Seat
from app.models.schemas.user import User

@pytest.fixture
def db():
    return AsyncMock()


@pytest.fixture
def repo(db):
    return TrainRepository(db)


@pytest.mark.asyncio
async def test_find_train_by_id(db, repo):

    result = MagicMock()
    train = MagicMock()

    result.scalar_one_or_none.return_value = train
    db.execute.return_value = result

    response = await repo.find_train_by_id(1)

    assert response == train


@pytest.mark.asyncio
async def test_find_train_by_number(db, repo):

    result = MagicMock()
    train = MagicMock()

    result.scalar_one_or_none.return_value = train
    db.execute.return_value = result

    response = await repo.find_train_by_number("12345")

    assert response == train


@pytest.mark.asyncio
async def test_add_train(db, repo):

    train = MagicMock()

    response = await repo.add_train(train)

    assert response == train

    db.add.assert_called_once_with(train)
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_coach(db, repo):

    result = MagicMock()
    coach = MagicMock()

    result.scalar_one_or_none.return_value = coach
    db.execute.return_value = result

    response = await repo.find_coach(1)

    assert response == coach


@pytest.mark.asyncio
async def test_find_all_train_on_journey_date(db, repo):

    result = MagicMock()

    trains = [
        MagicMock(),
        MagicMock()
    ]

    result.scalars.return_value.all.return_value = trains
    db.execute.return_value = result

    response = await repo.find_all_train_on_journey_date(
        "2026-09-20"
    )

    assert response == trains


@pytest.mark.asyncio
async def test_get_all_trains(db, repo):

    result = MagicMock()

    trains = [
        MagicMock(),
        MagicMock()
    ]

    result.scalars.return_value.all.return_value = trains
    db.execute.return_value = result

    response = await repo.get_all_trains()

    assert response == trains