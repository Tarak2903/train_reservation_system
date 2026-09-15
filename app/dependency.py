from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.helpers.database import get_db
from app.repositories.CoachRepository import CoachRepository
from app.repositories.AuthRepository import AuthRepository
from app.repositories.JourneyRepository import JourneyRepository
from app.repositories.SeatRepository import SeatRepository
from app.repositories.TrainRepository import TrainRepository
from app.repositories.BookingRepository import BookingRepository
from app.services.AuthService import AuthService
from app.services.CoachService import CoachService
from app.services.JourneyService import JourneyService
from app.services.TrainService import TrainService
from app.services.BookingService import BookingService

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