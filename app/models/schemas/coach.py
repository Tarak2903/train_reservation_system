from sqlalchemy import Column, Integer, String, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.helpers.database import Base
from app.models.enums import CoachClass


class Coach(Base):
    __tablename__ = "coaches"

    id = Column(Integer, primary_key=True, index=True)
    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False, index=True)
    coach_number = Column(String, nullable=False)
    class_type = Column(Enum(CoachClass, name="coach_class"), nullable=False)
    total_seat_capacity = Column(Integer, nullable=False)
    rac_capacity = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("train_id", "coach_number", name="uq_train_coach"),
    )

    train = relationship("Train", back_populates="coaches")
    seats = relationship("Seat", back_populates="coach")
