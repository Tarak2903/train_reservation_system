from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.helpers.database import get_db
from app.repositories.AuthRepository import AuthRepository
from app.repositories.TrainRepository import TrainRepository
from app.repositories.BookingRepository import BookingRepository
from app.services.AuthService import AuthService
from app.services.TrainService import TrainService
from app.services.BookingService import BookingService


async def get_auth_repository(db: AsyncSession = Depends(get_db)):
    return AuthRepository(db)


async def get_auth_service(auth_repo: AuthRepository = Depends(get_auth_repository)):
    return AuthService(auth_repo)


async def get_train_repository(db: AsyncSession = Depends(get_db)):
    return TrainRepository(db)


async def get_train_service(train_repo: TrainRepository = Depends(get_train_repository)):
    return TrainService(train_repo)


async def get_booking_repository(db: AsyncSession = Depends(get_db)):
    return BookingRepository(db)


async def get_booking_service(booking_repo: BookingRepository = Depends(get_booking_repository),train_repo: TrainRepository = Depends(get_train_repository)):
    return BookingService(booking_repo, train_repo)
