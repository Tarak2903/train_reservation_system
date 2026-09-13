from pydantic import BaseModel, Field


class TrainCreationRequest(BaseModel):
    train_number: str =Field(max_length=5,min_length=5)
    train_name: str =Field(min_length=2)
    source: str=Field(min_length=2)
    destination: str=Field(min_length=2)
    departure_time: str
    arrival_time: str
