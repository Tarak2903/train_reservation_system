from pydantic import BaseModel, Field
from app.models.enums import CoachClass


class CoachCreationRequest(BaseModel):
    coach_number: str
    class_type: CoachClass
    total_seat_capacity: int = Field(gt=0)
    rac_capacity: int = Field(ge=0)
