from pydantic import BaseModel


class CoachResponse(BaseModel):
    coach_number: str
    class_type: str
    total_seat_capacity: int
    rac_capacity: int
