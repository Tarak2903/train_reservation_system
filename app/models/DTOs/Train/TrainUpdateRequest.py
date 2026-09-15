from datetime import time

from pydantic import BaseModel, Field, model_validator


class TrainUpdateRequest(BaseModel):
    train_number: str | None = Field(default=None, min_length=5, max_length=5)
    train_name: str | None = Field(default=None, min_length=2)
    source: str | None = Field(default=None, min_length=2)
    destination: str | None = Field(default=None, min_length=2)
    departure_time: time | None = None
    arrival_time: time | None = None

    @model_validator(mode="after")
    def validate_time(self):
        if (
            self.arrival_time is not None
            and self.departure_time is not None
            and self.arrival_time >= self.departure_time
        ):
            raise ValueError(
                "Arrival time cannot be greater or equal to departure time"
            )

        return self