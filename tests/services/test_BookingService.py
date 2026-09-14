from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions.ResourceNotFoundException import ResourceNotFoundException
from app.exceptions.ResrouceAlreadyExistsException import ResourceAlreadyExistsException
from app.exceptions.booking_exceptions import BookingOperationException
from app.models.enums import BookingStatus, CoachClass, PassengerStatus
from app.services.BookingService import BookingService


@pytest.fixture
def repos():
    return AsyncMock(), AsyncMock(), AsyncMock()


@pytest.fixture
def service(repos):
    booking_repo, train_repo, journey_repo = repos
    return BookingService(booking_repo, train_repo, journey_repo)


def test_generate_pnr_is_nine_digit_string():
    pnr = BookingService.generate_pnr()
    assert pnr.isdigit()
    assert len(pnr) == 9
    assert 100000000 <= int(pnr) <= 999999999


@pytest.mark.asyncio
async def test_get_available_seats_filters_occupied_seats(service, repos):
    booking_repo, _, _ = repos
    seats = [SimpleNamespace(id=1), SimpleNamespace(id=2), SimpleNamespace(id=3)]
    booking_repo.get_occupied_seat_ids.return_value = {2}
    booking_repo.get_seats.return_value = seats

    result = await service._get_available_seats(1, date(2026, 9, 15), CoachClass.SLEEPER)

    assert [seat.id for seat in result] == [1, 3]


@pytest.mark.asyncio
async def test_next_sequence_delegates_to_repository(service, repos):
    booking_repo, _, _ = repos
    booking_repo.get_next_sequence.return_value = 7

    result = await service._next_sequence(5, CoachClass.SLEEPER, PassengerStatus.RAC)

    assert result == 7
    booking_repo.get_next_sequence.assert_awaited_once_with(
        5, CoachClass.SLEEPER, PassengerStatus.RAC
    )


@pytest.mark.asyncio
async def test_validate_cancellation_request_raises_for_cancelled_booking(service, repos):
    booking_repo, _, _ = repos
    booking_repo.find_booking.return_value = SimpleNamespace(
        status=BookingStatus.CANCELLED,
        user_id=1,
    )

    with pytest.raises(BookingOperationException, match="Booking already inactive"):
        await service.validate_cancellation_request(10, 1)


@pytest.mark.asyncio
@pytest.mark.xfail(raises=AttributeError, strict=True, reason="Current implementation checks booking.status before checking booking is None")
async def test_validate_cancellation_request_raises_for_missing_booking(service, repos):
    booking_repo, _, _ = repos
    booking_repo.find_booking.return_value = None

    # The current implementation accesses booking.status before checking
    # whether booking is None. This test documents the intended behavior.
    with pytest.raises(BookingOperationException, match="Booking Not found"):
        await service.validate_cancellation_request(10, 1)


@pytest.mark.asyncio
async def test_validate_cancellation_request_raises_for_wrong_user(service, repos):
    booking_repo, _, _ = repos
    booking_repo.find_booking.return_value = SimpleNamespace(
        status=BookingStatus.ACTIVE,
        user_id=2,
    )

    with pytest.raises(BookingOperationException, match="only cancel"):
        await service.validate_cancellation_request(10, 1)


@pytest.mark.asyncio
async def test_validate_cancellation_request_returns_booking(service, repos):
    booking_repo, _, _ = repos
    booking = SimpleNamespace(status=BookingStatus.ACTIVE, user_id=1)
    booking_repo.find_booking.return_value = booking

    result = await service.validate_cancellation_request(10, 1)

    assert result is booking


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

    assert await service.validate_train_by_id(1) is train


@pytest.mark.asyncio
async def test_validate_journey_raises_when_missing(service, repos):
    _, _, journey_repo = repos
    journey_repo.find_schedule.return_value = None

    with pytest.raises(BookingOperationException):
        await service.validate_journey(1, date(2026, 9, 15))


@pytest.mark.asyncio
async def test_validate_journey_returns_journey(service, repos):
    _, _, journey_repo = repos
    journey = MagicMock()
    journey_repo.find_schedule.return_value = journey

    assert await service.validate_journey(1, date(2026, 9, 15)) is journey


@pytest.mark.asyncio
async def test_validate_booking_request_rejects_duplicate_passengers(service, repos):
    request = SimpleNamespace(passenger_ids=[1, 1], train_id=10, journey_date=date(2026, 9, 15))

    with pytest.raises(BookingOperationException, match="Duplicate"):
        await service.validate_booking_request(request)


@pytest.mark.asyncio
async def test_validate_booking_request_rejects_missing_passenger(service, repos):
    booking_repo, _, _ = repos
    booking_repo.find_user.return_value = None
    request = SimpleNamespace(passenger_ids=[1], train_id=10, journey_date=date(2026, 9, 15))

    with pytest.raises(ResourceNotFoundException, match="Passenger 1"):
        await service.validate_booking_request(request)


@pytest.mark.asyncio
async def test_validate_booking_request_rejects_already_booked_passenger(service, repos):
    booking_repo, _, _ = repos
    booking_repo.find_user.return_value = MagicMock()
    booking_repo.find_active_passenger_on_journey.return_value = MagicMock()
    request = SimpleNamespace(passenger_ids=[1], train_id=10, journey_date=date(2026, 9, 15))

    with pytest.raises(ResourceAlreadyExistsException, match="Passenger 1"):
        await service.validate_booking_request(request)


@pytest.mark.asyncio
async def test_validate_booking_request_returns_unique_passengers(service, repos):
    booking_repo, _, _ = repos
    booking_repo.find_user.return_value = MagicMock()
    booking_repo.find_active_passenger_on_journey.return_value = None
    request = SimpleNamespace(passenger_ids=[1, 2], train_id=10, journey_date=date(2026, 9, 15))

    assert await service.validate_booking_request(request) == [1, 2]
    assert booking_repo.find_user.await_count == 2


def test_validate_booking_availability_rejects_insufficient_confirmed_seats():
    request = SimpleNamespace(booking_status=PassengerStatus.CNF)

    with pytest.raises(BookingOperationException, match="Not enough confirmed"):
        BookingService.validate_booking_availability(request, 1, 2, 0, 2)


def test_validate_booking_availability_allows_confirmed_booking_when_capacity_exists():
    request = SimpleNamespace(booking_status=PassengerStatus.CNF)
    BookingService.validate_booking_availability(request, 2, 2, 0, 2)


def test_validate_booking_availability_rejects_rac_when_confirmed_seats_exist():
    request = SimpleNamespace(booking_status=PassengerStatus.RAC)

    with pytest.raises(BookingOperationException, match="RAC booking is not allowed"):
        BookingService.validate_booking_availability(request, 1, 1, 0, 2)


def test_validate_booking_availability_rejects_rac_when_capacity_is_full():
    request = SimpleNamespace(booking_status=PassengerStatus.RAC)

    with pytest.raises(BookingOperationException, match="Not enough RAC"):
        BookingService.validate_booking_availability(request, 0, 2, 1, 2)


def test_validate_booking_availability_allows_rac_when_capacity_exists():
    request = SimpleNamespace(booking_status=PassengerStatus.RAC)
    BookingService.validate_booking_availability(request, 0, 2, 0, 2)


def test_validate_booking_availability_rejects_waitlist_when_confirmed_exists():
    request = SimpleNamespace(booking_status=PassengerStatus.WL)

    with pytest.raises(BookingOperationException, match="Waitlist booking is not allowed"):
        BookingService.validate_booking_availability(request, 1, 1, 2, 2)


def test_validate_booking_availability_rejects_waitlist_when_rac_capacity_available():
    request = SimpleNamespace(booking_status=PassengerStatus.WL)

    with pytest.raises(BookingOperationException, match="Waitlist booking is not allowed"):
        BookingService.validate_booking_availability(request, 0, 1, 1, 2)


def test_validate_booking_availability_allows_waitlist_when_rac_full():
    request = SimpleNamespace(booking_status=PassengerStatus.WL)
    BookingService.validate_booking_availability(request, 0, 1, 2, 2)


@pytest.mark.asyncio
async def test_book_confirm_ticket_adds_confirmed_passengers(service, repos):
    booking_repo, _, _ = repos
    booking = SimpleNamespace(id=100)
    seats = [SimpleNamespace(id=10), SimpleNamespace(id=11)]

    message = await service.book_confirm_ticket(booking, [1, 2], seats)

    assert message == "Ticket booked successfully"
    assert booking_repo.add_passenger.await_count == 2
    passengers = [call.args[0] for call in booking_repo.add_passenger.await_args_list]
    assert [p.passenger_id for p in passengers] == [1, 2]
    assert [p.seat_id for p in passengers] == [10, 11]
    assert all(p.status is PassengerStatus.CNF for p in passengers)


@pytest.mark.asyncio
async def test_book_rac_ticket_assigns_incrementing_sequences(service, repos):
    booking_repo, _, _ = repos
    booking_repo.get_next_sequence.return_value = 5
    booking = SimpleNamespace(id=100)
    schedule = SimpleNamespace(id=20)

    message = await service.book_rac_ticket(booking, schedule, CoachClass.SLEEPER, [1, 2, 3])

    assert message == "Ticket booked in RAC"
    passengers = [call.args[0] for call in booking_repo.add_passenger.await_args_list]
    assert [p.queue_sequence for p in passengers] == [5, 6, 7]
    assert all(p.status is PassengerStatus.RAC for p in passengers)


@pytest.mark.asyncio
async def test_book_waiting_ticket_assigns_incrementing_sequences(service, repos):
    booking_repo, _, _ = repos
    booking_repo.get_next_sequence.return_value = 8
    booking = SimpleNamespace(id=100)
    schedule = SimpleNamespace(id=20)

    message = await service.book_waiting_ticket(booking, schedule, CoachClass.SLEEPER, [1, 2])

    assert message == "Ticket booked in waitlist"
    passengers = [call.args[0] for call in booking_repo.add_passenger.await_args_list]
    assert [p.queue_sequence for p in passengers] == [8, 9]
    assert all(p.status is PassengerStatus.WL for p in passengers)


@pytest.mark.asyncio
async def test_book_ticket_confirmed_path(service, repos):
    booking_repo, train_repo, journey_repo = repos
    train_repo.find_train_by_id.return_value = MagicMock()
    schedule = SimpleNamespace(id=20)
    journey_repo.find_schedule.return_value = schedule
    booking_repo.find_user.return_value = MagicMock()
    booking_repo.find_active_passenger_on_journey.return_value = None
    booking_repo.get_occupied_seat_ids.return_value = set()
    booking_repo.get_seats.return_value = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
    booking_repo.get_queue_count.return_value = 0
    booking_repo.get_total_rac_capacity.return_value = 2
    stored_booking = MagicMock()
    booking_repo.find_booking.return_value = stored_booking
    booking_repo.add_booking.side_effect = lambda booking: setattr(booking, "id", 99)

    request = SimpleNamespace(
        train_id=1,
        journey_date=date(2026, 9, 15),
        class_type=CoachClass.SLEEPER,
        booking_status=PassengerStatus.CNF,
        passenger_ids=[10, 11],
    )

    with patch.object(service, "generate_pnr", return_value="123456789"):
        result, message = await service.book_ticket(request, 7)

    assert result is stored_booking
    assert message == "Ticket booked successfully"
    booking_repo.commit.assert_awaited_once()
    assert booking_repo.add_passenger.await_count == 2


@pytest.mark.asyncio
async def test_book_ticket_rac_path(service, repos):
    booking_repo, train_repo, journey_repo = repos
    train_repo.find_train_by_id.return_value = MagicMock()
    journey_repo.find_schedule.return_value = SimpleNamespace(id=20)
    booking_repo.find_user.return_value = MagicMock()
    booking_repo.find_active_passenger_on_journey.return_value = None
    booking_repo.get_occupied_seat_ids.return_value = set()
    booking_repo.get_seats.return_value = []
    booking_repo.get_queue_count.return_value = 0
    booking_repo.get_total_rac_capacity.return_value = 2
    booking_repo.get_next_sequence.return_value = 1
    booking_repo.find_booking.return_value = MagicMock()
    booking_repo.add_booking.side_effect = lambda booking: setattr(booking, "id", 99)

    request = SimpleNamespace(
        train_id=1,
        journey_date=date(2026, 9, 15),
        class_type=CoachClass.SLEEPER,
        booking_status=PassengerStatus.RAC,
        passenger_ids=[10],
    )

    with patch.object(service, "generate_pnr", return_value="123456789"):
        result, message = await service.book_ticket(request, 7)

    assert message == "Ticket booked in RAC"
    assert result is booking_repo.find_booking.return_value


@pytest.mark.asyncio
async def test_cancel_confirm_ticket_promotes_rac_and_waiting(service, repos):
    booking_repo, _, _ = repos
    booking = SimpleNamespace(
        id=100,
        train_id=1,
        schedule_id=20,
        class_type=CoachClass.SLEEPER,
        passengers=[
            SimpleNamespace(seat_id=10),
            SimpleNamespace(seat_id=11),
        ],
    )
    rac = [SimpleNamespace(queue_sequence=3, seat_id=None, status=PassengerStatus.RAC)]
    waiting_for_cnf = [SimpleNamespace(queue_sequence=7, seat_id=None, status=PassengerStatus.WL)]
    waiting_for_rac = [SimpleNamespace(queue_sequence=8, seat_id=None, status=PassengerStatus.WL)]
    booking_repo.find_top_k_status_passengers.side_effect = [rac, waiting_for_cnf, waiting_for_rac]
    booking_repo.db = AsyncMock()

    await service.cancel_confirm_ticket(booking)

    assert rac[0].status is PassengerStatus.CNF
    assert rac[0].seat_id == 10
    assert rac[0].queue_sequence is None
    assert waiting_for_cnf[0].status is PassengerStatus.CNF
    assert waiting_for_cnf[0].seat_id == 11
    assert waiting_for_rac[0].status is PassengerStatus.RAC
    assert booking_repo.db.flush.await_count == 2


@pytest.mark.asyncio
async def test_promote_waiting_passengers_changes_status_to_rac(service, repos):
    booking_repo, _, _ = repos
    booking = SimpleNamespace(
        train_id=1,
        schedule_id=20,
        class_type=CoachClass.SLEEPER,
        passengers=[SimpleNamespace(id=1), SimpleNamespace(id=2)],
    )
    waiting = [SimpleNamespace(status=PassengerStatus.WL)]
    booking_repo.find_top_k_status_passengers.return_value = waiting
    booking_repo.db = AsyncMock()

    await service.promote_waiting_passengers(booking)

    assert waiting[0].status is PassengerStatus.RAC
    booking_repo.find_top_k_status_passengers.assert_awaited_once_with(
        booking, 2, PassengerStatus.WL
    )
    booking_repo.db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_cancel_ticket_marks_booking_and_passengers_cancelled(service, repos):
    booking_repo, _, _ = repos
    passengers = [
        SimpleNamespace(status=PassengerStatus.RAC, seat_id=10, queue_sequence=1),
        SimpleNamespace(status=PassengerStatus.RAC, seat_id=11, queue_sequence=2),
    ]
    booking = SimpleNamespace(
        status=BookingStatus.ACTIVE,
        user_id=7,
        passengers=passengers,
    )
    booking_repo.find_booking.return_value = booking
    booking_repo.db = AsyncMock()

    with patch.object(service, "cancel_rac_ticket", new=AsyncMock()) as cancel_rac:
        result = await service.cancel_ticket(50, 7)

    assert result is booking
    assert booking.status is BookingStatus.CANCELLED
    for passenger in passengers:
        assert passenger.status is PassengerStatus.CANCELLED
        assert passenger.seat_id is None
        assert passenger.queue_sequence is None
    cancel_rac.assert_awaited_once_with(booking)
    booking_repo.db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_booking_status_returns_valid_booking(service, repos):
    booking_repo, _, _ = repos
    booking = SimpleNamespace(status=BookingStatus.ACTIVE, user_id=7)
    booking_repo.find_booking.return_value = booking

    result = await service.get_booking_status(50, 7)

    assert result is booking


@pytest.mark.asyncio
async def test_get_queue_validates_train_and_journey_then_returns_queue(service, repos):
    booking_repo, train_repo, journey_repo = repos
    train_repo.find_train_by_id.return_value = MagicMock()
    journey_repo.find_schedule.return_value = MagicMock()
    queue = [MagicMock()]
    booking_repo.get_active_queue.return_value = queue

    result = await service.get_queue(1, date(2026, 9, 15), CoachClass.SLEEPER, PassengerStatus.RAC)

    assert result == queue
    booking_repo.get_active_queue.assert_awaited_once_with(
        1, date(2026, 9, 15), CoachClass.SLEEPER, PassengerStatus.RAC
    )


@pytest.mark.asyncio
async def test_get_availability_returns_counts(service, repos):
    booking_repo, train_repo, journey_repo = repos
    train_repo.find_train_by_id.return_value = MagicMock()
    journey_repo.find_schedule.return_value = SimpleNamespace(id=20)
    booking_repo.get_total_seat_count.return_value = 10
    booking_repo.get_confirmed_count.return_value = 4
    booking_repo.get_total_rac_capacity.return_value = 3
    booking_repo.get_queue_count.side_effect = [2, 1]

    result = await service.get_availability(1, date(2026, 9, 15), CoachClass.SLEEPER)

    assert result == {
        "train_id": 1,
        "journey_date": date(2026, 9, 15),
        "class_type": "SL",
        "total_seats": 10,
        "confirmed": 4,
        "available": 6,
        "rac_capacity": 3,
        "rac": 2,
        "waitlist": 1,
    }
