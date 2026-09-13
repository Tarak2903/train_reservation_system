from pydantic import BaseModel


class SeatResponse(BaseModel):
    seat_id: int
    coach_id: int
    seat_number: int
