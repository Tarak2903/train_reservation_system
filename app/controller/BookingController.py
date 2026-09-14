from datetime import date

from fastapi import APIRouter, Depends

from app.dependency import get_booking_service, get_train_service
from app.models.enums import PassengerStatus, CoachClass
from app.auth import get_current_user
from app.models.schemas.user import User
from app.models.DTOs.APIResponse import APIResponse
from app.models.DTOs.Booking.BookingRequest import BookingRequest
from app.models.DTOs.Booking.BookingResponse import BookingResponse, PassengerResponse
from app.models.DTOs.Booking.AvailabilityResponse import AvailabilityResponse
from app.models.DTOs.Booking.QueueResponse import QueueResponse, QueuePassengerResponse
from app.services.BookingService import BookingService
from app.services.TrainService import TrainService

router = APIRouter()

def booking_response(booking):
    passengers = []

    for passenger in booking.passengers:
        coach_number = None
        seat_number = None

        if passenger.seat:
            seat_number = passenger.seat.seat_number
            coach_number = passenger.seat.coach.coach_number

        passengers.append(
            PassengerResponse(
                passenger_name=passenger.passenger.name,
                status=passenger.status.value,
                queue_sequence=passenger.queue_sequence,
                coach_number=coach_number,
                seat_number=seat_number
            )
        )

    return BookingResponse(
        pnr=booking.pnr,
        train_id=booking.train_id,
        journey_date=booking.journey_date,
        class_type=booking.class_type.value,
        booking_status=booking.status.value,
        booked_by=booking.user_id,
        passengers=passengers,
    )


@router.post("/bookings", response_model=APIResponse[BookingResponse], tags=["Booking"])
async def book_ticket(
    request: BookingRequest,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
):
    booking, message = await booking_service.book_ticket(request, current_user.id)

    return APIResponse(
        success=True,
        message=message,
        data= booking_response(booking),
    )


@router.delete("/bookings/{booking_id}", response_model=APIResponse[BookingResponse], tags=["Booking"])
async def cancel_ticket(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
):
    booking = await booking_service.cancel_ticket(
        booking_id,
        current_user.id,
    )

    return APIResponse(
        success=True,
        message="Ticket cancelled successfully",
        data= booking_response(booking),
    )


@router.get("/bookings/{booking_id}", response_model=APIResponse[BookingResponse], tags=["Booking"])
async def get_booking_status(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
):
    booking = await booking_service.get_booking_status(
        booking_id,
        current_user.id,
    )

    return APIResponse(
        success=True,
        message="Booking details retrieved successfully",
        data= booking_response(booking),
    )


@router.get("/availability", response_model=APIResponse[AvailabilityResponse], tags=["Booking"])
async def get_availability(
    train_id: int,
    journey_date: date,
    class_type: CoachClass,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
):
    result = await booking_service.get_availability(train_id, journey_date, class_type)

    return APIResponse(
        success=True,
        message="Availability retrieved successfully",
        data=AvailabilityResponse(**result),
    )


