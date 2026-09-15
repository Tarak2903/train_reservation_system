from datetime import time

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, model_validator


class TrainCreationRequest(BaseModel):
    train_number: str =Field(max_length=5,min_length=5)
    train_name: str =Field(min_length=2)
    source: str=Field(min_length=2)
    destination: str=Field(min_length=2)
    departure_time: time
    arrival_time: time

    @model_validator(mode="after")
    def validate_time(self):
        if self.arrival_time>=self.departure_time:
            raise ValueError("Arrival time cannot be greater or equal to departure time")

        return self

