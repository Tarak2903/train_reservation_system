from pydantic import BaseModel


class TrainResponse(BaseModel):
    train_number: str
    train_name: str
    source: str
    destination: str
    departure_time: str
    arrival_time: str
