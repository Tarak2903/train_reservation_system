from datetime import date
from pydantic import BaseModel


class QueuePassengerResponse(BaseModel):
    passenger_id: int
    passenger_name: str
    status: str
    queue_sequence: int
    pnr: str


class QueueResponse(BaseModel):
    train_id: int
    journey_date: date
    class_type: str
    status: str
    passengers: list[QueuePassengerResponse]
