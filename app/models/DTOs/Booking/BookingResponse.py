from datetime import date, datetime
from pydantic import BaseModel


class PassengerResponse(BaseModel):
    passenger_name: str
    status: str
    queue_sequence: int | None = None
    coach_number: str | None = None
    # seat_number: str | None = None


class BookingResponse(BaseModel):
    pnr: str
    train_id: int
    journey_date: date
    class_type: str
    booking_status: str
    booked_by: int
    passengers: list[PassengerResponse]
