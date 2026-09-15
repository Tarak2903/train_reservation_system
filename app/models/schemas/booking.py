from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from app.helpers.database import Base
from app.models.enums import BookingStatus, PassengerStatus, CoachClass


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    pnr = Column(String, nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False, index=True)
    schedule_id = Column(Integer, ForeignKey("train_schedule.id"), nullable=False, index=True)
    journey_date = Column(Date, nullable=False, index=True)
    class_type = Column(Enum(CoachClass, name="booking_class"), nullable=False)
    status = Column(Enum(BookingStatus, name="booking_status"), nullable=False)

    train = relationship("Train", back_populates="bookings")
    schedule = relationship("TrainSchedule", back_populates="bookings")
    booker = relationship("User")
    passengers = relationship("BookingPassenger", back_populates="booking")


class BookingPassenger(Base):
    __tablename__ = "booking_passengers"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False, index=True)
    passenger_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(Enum(PassengerStatus, name="passenger_status"), nullable=False)
    queue_sequence = Column(Integer, nullable=True, index=True)
    seat_id = Column(Integer, ForeignKey("seats.id"), nullable=True, index=True)

    __table_args__ = (
        UniqueConstraint("booking_id", "passenger_id", name="uq_booking_passenger"),
    )

    booking = relationship("Booking", back_populates="passengers")
    passenger = relationship("User")
    seat = relationship("Seat", back_populates="booking_passengers")
