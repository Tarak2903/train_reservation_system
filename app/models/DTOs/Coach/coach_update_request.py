from pydantic import BaseModel, Field
from app.models.enums import CoachClass


class CoachUpdateRequest(BaseModel):
    coach_number: str | None = None
    class_type: CoachClass | None = None
    total_seat_capacity: int | None = Field(default=None, gt=0)
    rac_capacity: int | None = Field(default=None, ge=0)