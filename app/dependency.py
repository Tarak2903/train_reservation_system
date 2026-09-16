from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.helpers.database import get_db
from app.repositories.coach_repository import CoachRepository
from app.repositories.auth_repository import AuthRepository
from app.repositories.journey_repository import JourneyRepository
from app.repositories.seat_repository import SeatRepository
from app.repositories.train_repository import TrainRepository
from app.repositories.booking_repository import BookingRepository
from app.services.auth_service import AuthService
from app.services.coach_service import CoachService
from app.services.journey_service import JourneyService
from app.services.train_service import TrainService
from app.services.booking_service import BookingService

def get_auth_repository(db:AsyncSession=Depends(get_db)):
    return AuthRepository(db)

def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(AuthRepository(db))

def get_train_service(db: AsyncSession = Depends(get_db)):
    return TrainService(TrainRepository(db),JourneyRepository(db),CoachRepository(db))


def get_booking_service(db: AsyncSession = Depends(get_db)):
    return BookingService(BookingRepository(db), TrainRepository(db),JourneyRepository(db))

def  get_coach_service(db:AsyncSession=Depends(get_db)):
    return CoachService(CoachRepository(db),TrainRepository(db),SeatRepository(db))

def get_journey_service(db:AsyncSession=Depends(get_db)):
    return JourneyService(JourneyRepository(db),TrainRepository(db))