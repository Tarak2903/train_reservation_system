from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.helpers.database import Base


class TrainSchedule(Base):
    __tablename__ = "train_schedule"

    id = Column(Integer, primary_key=True, index=True)
    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False, index=True)
    journey_date = Column(Date, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("train_id", "journey_date", name="uq_train_journey"),
    )

    train = relationship("Train", back_populates="schedules")
    bookings = relationship("Booking", back_populates="schedule")
