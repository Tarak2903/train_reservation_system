from datetime import time

from pydantic import BaseModel


class TrainResponse(BaseModel):
    train_number: str
    train_name: str
    source: str
    destination: str
    departure_time: time
    arrival_time: time
