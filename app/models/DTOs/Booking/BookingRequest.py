from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from app.models.enums import CoachClass, PassengerStatus


class BookingRequest(BaseModel):
    train_id: int
    journey_date: date
    class_type: CoachClass
    booking_status: PassengerStatus
    passenger_ids: list[int] = Field(min_length=1)
