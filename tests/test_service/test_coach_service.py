import  pytest
from unittest.mock import MagicMock,AsyncMock
from app.exceptions.ResourceNotFoundException import ResourceNotFoundException
from app.exceptions.ResrouceAlreadyExistsException import ResourceAlreadyExistsException
from app.exceptions.train_exceptions import TrainNotFoundException
from app.services.coach_service import CoachService


@pytest.fixture
def repos():
    return AsyncMock(),AsyncMock(),AsyncMock()


@pytest.fixture
def service(repos):
    coach_repo,train_repo,seat_repo=repos
    return CoachService(coach_repo, train_repo, seat_repo)


@pytest.mark.asyncio
async def test_validate_train_by_id_not_found(repos, service):
    coach_repo, train_repo, seat_repo = repos

    train_repo.find_train_by_id.return_value = None

    with pytest.raises(ResourceNotFoundException):
        await service.validate_train_by_id(10)


@pytest.mark.asyncio
async def test_validate_train_by_number_not_found(repos, service):
    coach_repo, train_repo, seat_repo = repos

    train_repo.find_train_by_number.return_value = None

    with pytest.raises(TrainNotFoundException):
        await service.validate_train_by_number(12345)


@pytest.mark.asyncio
async def test_add_coach_already_exists(repos, service):
    coach_repo, train_repo, seat_repo = repos

    train_repo.find_train_by_id.return_value = MagicMock()
    coach_repo.find_coach_by_coach_number_and_train_id.return_value = MagicMock()

    request = MagicMock()
    request.coach_number = "A01"

    with pytest.raises(ResourceAlreadyExistsException):
        await service.add_coach(10, request)


@pytest.mark.asyncio
async def test_add_seat_coach_not_found(repos, service):
    coach_repo, train_repo, seat_repo = repos

    train_repo.find_coach.return_value = None

    with pytest.raises(ResourceNotFoundException):
        await service.add_seat(10, 5)


@pytest.mark.asyncio
async def test_get_coaches_no_coaches(repos, service):
    coach_repo, train_repo, seat_repo = repos

    train_repo.find_train_by_number.return_value = MagicMock()
    coach_repo.get_coaches_by_train_number.return_value = None

    with pytest.raises(ResourceNotFoundException):
        await service.get_coaches_by_train_number(12345)


@pytest.mark.asyncio
async def test_update_coach_not_found(repos, service):
    coach_repo, train_repo, seat_repo = repos

    coach_repo.find_coach_by_id.return_value = None

    request = MagicMock()

    with pytest.raises(ResourceNotFoundException):
        await service.update_coach(10, 20, request)


@pytest.mark.asyncio
async def test_update_coach_wrong_train(repos, service):
    coach_repo, train_repo, seat_repo = repos

    coach = MagicMock()
    coach.train_id = 99

    coach_repo.find_coach_by_id.return_value = coach

    request = MagicMock()

    with pytest.raises(ResourceNotFoundException):
        await service.update_coach(10, 20, request)
