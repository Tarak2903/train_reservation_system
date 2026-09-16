from datetime import date
from pydantic import BaseModel


class AvailabilityResponse(BaseModel):
    train_id: int
    journey_date: date
    class_type: str
    total_seats: int
    confirmed: int
    available: int
    rac_capacity: int
    rac: int
    waitlist: int
