from datetime import date
from pydantic import BaseModel


class JourneyCreationRequest(BaseModel):
    journey_date: date
