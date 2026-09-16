import pytest
from unittest.mock import AsyncMock, MagicMock
from app.models.schemas.train import Train
from app.models.schemas.train_schedule import TrainSchedule
from app.models.schemas.coach import Coach
from app.models.schemas.seat import Seat
from app.models.schemas.user import User
from app.services.booking_service import BookingService
from app.models.enums import BookingStatus, PassengerStatus

from app.exceptions.ResrouceAlreadyExistsException import ResourceAlreadyExistsException
from app.exceptions.ResourceNotFoundException import ResourceNotFoundException
from app.exceptions.booking_exceptions import BookingOperationException


@pytest.fixture
def repos():
    return AsyncMock(), AsyncMock(), AsyncMock()


@pytest.fixture
def service(repos):
    booking_repo, train_repo, journey_repo = repos
    return BookingService(booking_repo, train_repo, journey_repo)


@pytest.mark.asyncio
async def test_get_available_seats(repos, service):
    booking_repo, train_repo, journey_repo = repos

    seat1 = MagicMock()
    seat1.id = 1

    seat2 = MagicMock()
    seat2.id = 2

    booking_repo.get_occupied_seat_ids.return_value = []
    booking_repo.get_seats.return_value = [seat1, seat2]
    booking_repo.try_lock_seat.return_value = True
    booking_repo.get_occupied_seat_ids.return_value = []

    result = await service._get_available_seats(
        10,
        "2026-09-20",
        "SL",
        2
    )

    assert result == [seat1, seat2]


@pytest.mark.asyncio
async def test_next_sequence(repos, service):
    booking_repo, train_repo, journey_repo = repos

    booking_repo.get_next_sequence.return_value = 5

    result = await service._next_sequence(
        1,
        "SL",
        PassengerStatus.RAC
    )

    assert result == 5


@pytest.mark.asyncio
async def test_validate_train_by_id(repos, service):
    booking_repo, train_repo, journey_repo = repos

    train = MagicMock()
    train_repo.find_train_by_id.return_value = train

    result = await service.validate_train_by_id(10)

    assert result == train


@pytest.mark.asyncio
async def test_validate_train_by_id_not_found(repos, service):
    booking_repo, train_repo, journey_repo = repos

    train_repo.find_train_by_id.return_value = None

    with pytest.raises(ResourceNotFoundException):
        await service.validate_train_by_id(10)


@pytest.mark.asyncio
async def test_validate_journey(repos, service):
    booking_repo, train_repo, journey_repo = repos

    journey = MagicMock()
    journey_repo.find_schedule.return_value = journey

    result = await service.validate_journey(
        10,
        "2026-09-20"
    )

    assert result == journey


@pytest.mark.asyncio
async def test_validate_journey_not_found(repos, service):
    booking_repo, train_repo, journey_repo = repos

    journey_repo.find_schedule.return_value = None

    with pytest.raises(BookingOperationException):
        await service.validate_journey(
            10,
            "2026-09-20"
        )


@pytest.mark.asyncio
async def test_validate_booking_request(repos, service):
    booking_repo, train_repo, journey_repo = repos

    request = MagicMock()
    request.passenger_ids = [1, 2]
    request.train_id = 10
    request.journey_date = "2026-09-20"

    booking_repo.find_user.return_value = MagicMock()
    booking_repo.find_active_passenger_on_journey.return_value = None

    result = await service.validate_booking_request(request)

    assert result == [1, 2]


@pytest.mark.asyncio
async def test_duplicate_passenger(repos, service):
    booking_repo, train_repo, journey_repo = repos

    request = MagicMock()
    request.passenger_ids = [1, 1]

    with pytest.raises(BookingOperationException):
        await service.validate_booking_request(request)


@pytest.mark.asyncio
async def test_passenger_not_found(repos, service):
    booking_repo, train_repo, journey_repo = repos

    request = MagicMock()
    request.passenger_ids = [1]
    request.train_id = 10
    request.journey_date = "2026-09-20"

    booking_repo.find_user.return_value = None

    with pytest.raises(ResourceNotFoundException):
        await service.validate_booking_request(request)


@pytest.mark.asyncio
async def test_passenger_already_booked(repos, service):
    booking_repo, train_repo, journey_repo = repos

    request = MagicMock()
    request.passenger_ids = [1]
    request.train_id = 10
    request.journey_date = "2026-09-20"

    booking_repo.find_user.return_value = MagicMock()
    booking_repo.find_active_passenger_on_journey.return_value = MagicMock()

    with pytest.raises(ResourceAlreadyExistsException):
        await service.validate_booking_request(request)


@pytest.mark.asyncio
async def test_validate_cancellation_request(repos, service):
    booking_repo, train_repo, journey_repo = repos

    booking = MagicMock()
    booking.status = BookingStatus.ACTIVE
    booking.user_id = 1

    booking_repo.find_booking.return_value = booking

    result = await service.validate_cancellation_request(10, 1)

    assert result == booking


@pytest.mark.asyncio
async def test_cancel_booking_already_cancelled(repos, service):
    booking_repo, train_repo, journey_repo = repos

    booking = MagicMock()
    booking.status = BookingStatus.CANCELLED

    booking_repo.find_booking.return_value = booking

    with pytest.raises(BookingOperationException):
        await service.validate_cancellation_request(10, 1)


@pytest.mark.asyncio
async def test_cancel_booking_wrong_user(repos, service):
    booking_repo, train_repo, journey_repo = repos

    booking = MagicMock()
    booking.status = BookingStatus.ACTIVE
    booking.user_id = 5

    booking_repo.find_booking.return_value = booking

    with pytest.raises(BookingOperationException):
        await service.validate_cancellation_request(10, 1)


def test_validate_booking_availability_cnf_success():
    request = MagicMock()
    request.booking_status = PassengerStatus.CNF

    BookingService.validate_booking_availability(
        request,
        confirmed_available=5,
        group_size=2,
        current_rac=0,
        rac_capacity=10
    )


def test_cnf_not_enough_seats():
    request = MagicMock()
    request.booking_status = PassengerStatus.CNF

    with pytest.raises(BookingOperationException):
        BookingService.validate_booking_availability(
            request,
            confirmed_available=1,
            group_size=2,
            current_rac=0,
            rac_capacity=10
        )


def test_validate_booking_availability_rac_success():
    request = MagicMock()
    request.booking_status = PassengerStatus.RAC

    BookingService.validate_booking_availability(
        request,
        confirmed_available=0,
        group_size=2,
        current_rac=3,
        rac_capacity=10
    )


def test_rac_while_confirmed_available():
    request = MagicMock()
    request.booking_status = PassengerStatus.RAC

    with pytest.raises(BookingOperationException):
        BookingService.validate_booking_availability(
            request,
            confirmed_available=5,
            group_size=1,
            current_rac=0,
            rac_capacity=10
        )


def test_rac_capacity_not_enough():
    request = MagicMock()
    request.booking_status = PassengerStatus.RAC

    with pytest.raises(BookingOperationException):
        BookingService.validate_booking_availability(
            request,
            confirmed_available=0,
            group_size=3,
            current_rac=8,
            rac_capacity=10
        )


def test_validate_booking_availability_wl_success():
    request = MagicMock()
    request.booking_status = PassengerStatus.WL

    BookingService.validate_booking_availability(
        request,
        confirmed_available=0,
        group_size=2,
        current_rac=10,
        rac_capacity=10
    )


def test_waiting_list_while_confirmed_available():
    request = MagicMock()
    request.booking_status = PassengerStatus.WL

    with pytest.raises(BookingOperationException):
        BookingService.validate_booking_availability(
            request,
            confirmed_available=5,
            group_size=1,
            current_rac=10,
            rac_capacity=10
        )


def test_waiting_list_while_rac_available():
    request = MagicMock()
    request.booking_status = PassengerStatus.WL

    with pytest.raises(BookingOperationException):
        BookingService.validate_booking_availability(
            request,
            confirmed_available=0,
            group_size=1,
            current_rac=5,
            rac_capacity=10
        )


@pytest.mark.asyncio
async def test_book_confirm_ticket(repos, service):
    booking_repo, train_repo, journey_repo = repos

    booking = MagicMock()

    passenger1 = 1
    passenger2 = 2

    seat1 = MagicMock()
    seat1.id = 101

    seat2 = MagicMock()
    seat2.id = 102

    result = await service.book_confirm_ticket(
        booking,
        [passenger1, passenger2],
        [seat1, seat2]
    )

    assert result == "Ticket booked successfully"
    assert booking_repo.add_passenger.await_count == 2


@pytest.mark.asyncio
async def test_book_rac_ticket(repos, service):
    booking_repo, train_repo, journey_repo = repos

    booking = MagicMock()
    schedule = MagicMock()
    schedule.id = 10

    booking_repo.get_next_sequence.return_value = 5

    result = await service.book_rac_ticket(
        booking,
        schedule,
        "SL",
        [1, 2]
    )

    assert result == "Ticket booked in RAC"
    assert booking_repo.add_passenger.await_count == 2


@pytest.mark.asyncio
async def test_book_waiting_ticket(repos, service):
    booking_repo, train_repo, journey_repo = repos

    booking = MagicMock()
    schedule = MagicMock()
    schedule.id = 10

    booking_repo.get_next_sequence.return_value = 5

    result = await service.book_waiting_ticket(
        booking,
        schedule,
        "SL",
        [1, 2]
    )

    assert result == "Ticket booked in waitlist"
    assert booking_repo.add_passenger.await_count == 2


@pytest.mark.asyncio
async def test_get_queue(repos, service):
    booking_repo, train_repo, journey_repo = repos

    train_repo.find_train_by_id.return_value = MagicMock()
    journey_repo.find_schedule.return_value = MagicMock()

    queue = [MagicMock()]
    booking_repo.get_active_queue.return_value = queue

    result = await service.get_queue(
        10,
        "2026-09-20",
        "SL",
        PassengerStatus.RAC
    )

    assert result == queue


@pytest.mark.asyncio
async def test_get_availability(repos, service):
    booking_repo, train_repo, journey_repo = repos

    train_repo.find_train_by_id.return_value = MagicMock()

    schedule = MagicMock()
    schedule.id = 100
    journey_repo.find_schedule.return_value = schedule

    booking_repo.get_total_seat_count.return_value = 10
    booking_repo.get_confirmed_count.return_value = 4
    booking_repo.get_total_rac_capacity.return_value = 5
    booking_repo.get_queue_count.side_effect = [2, 3]

    result = await service.get_availability(
        10,
        "2026-09-20",
        MagicMock(value="SL")
    )

    assert result["train_id"] == 10
    assert result["total_seats"] == 10
    assert result["confirmed"] == 4
    assert result["available"] == 6
    assert result["rac_capacity"] == 5
    assert result["rac"] == 2
    assert result["waitlist"] == 3


@pytest.mark.asyncio
async def test_get_all_trains_on_journey_date(repos, service):
    booking_repo, train_repo, journey_repo = repos

    trains = [MagicMock(), MagicMock()]
    train_repo.find_all_train_on_journey_date.return_value = trains

    result = await service.get_all_trains_on_journey_date(
        "2026-09-20"
    )

    assert result == trains


@pytest.mark.asyncio
async def test_get_all_trains_on_journey_date_not_found(repos, service):
    booking_repo, train_repo, journey_repo = repos

    train_repo.find_all_train_on_journey_date.return_value = []

    with pytest.raises(ResourceNotFoundException):
        await service.get_all_trains_on_journey_date(
            "2026-09-20"
        )
