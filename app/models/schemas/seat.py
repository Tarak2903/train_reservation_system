from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.helpers.database import Base


class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=False, index=True)
    seat_number = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("coach_id", "seat_number", name="uq_coach_seat"),
    )

    coach = relationship("Coach", back_populates="seats")
    booking_passengers = relationship("BookingPassenger", back_populates="seat")
