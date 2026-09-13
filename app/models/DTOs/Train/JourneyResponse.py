from datetime import date
from pydantic import BaseModel


class JourneyResponse(BaseModel):
    journey_id: int
    train_id: int
    journey_date: date
