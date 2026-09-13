from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.helpers.database import Base


class Train(Base):
    __tablename__ = "trains"

    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String, nullable=False, unique=True, index=True)
    train_name = Column(String, nullable=False)
    source = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_time = Column(String, nullable=False)
    arrival_time = Column(String, nullable=False)

    schedules = relationship("TrainSchedule", back_populates="train", cascade="all, delete-orphan")
    coaches = relationship("Coach", back_populates="train", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="train")
