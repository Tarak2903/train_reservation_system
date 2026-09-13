from pydantic import BaseModel, Field


class SeatCreationRequest(BaseModel):
    seat_count: int = Field(gt=0)
