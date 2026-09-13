from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.schemas.train import Train
from app.models.schemas.train_schedule import TrainSchedule
from app.models.schemas.coach import Coach


class TrainRepository:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def find_train_by_id(self, train_id):
        result = await self.db.execute(
            select(Train).where(Train.id == train_id)
        )
        return result.scalar_one_or_none()


    async def find_train_by_number(self, train_number):
        result = await self.db.execute(
            select(Train).where(Train.train_number == train_number)
        )
        return result.scalar_one_or_none()


    async def add_train(self, train):
        self.db.add(train)
        await self.db.flush()
        return train


    async def add_schedule(self, schedule):
        self.db.add(schedule)
        await self.db.flush()
        return schedule


    async def find_schedule(self, train_id, journey_date):
        result = await self.db.execute(
            select(TrainSchedule).where(
                TrainSchedule.train_id == train_id,
                TrainSchedule.journey_date == journey_date,
            )
        )
        return result.scalar_one_or_none()


    async def find_coach(self, coach_id):
        result = await self.db.execute(
            select(Coach)
            .options(selectinload(Coach.seats))
            .where(Coach.id == coach_id)
        )
        return result.scalar_one_or_none()


    async def get_coaches(self, train_id, class_type):
        result = await self.db.execute(
            select(Coach)
            .options(selectinload(Coach.seats))
            .where(
                Coach.train_id == train_id,
                Coach.class_type == class_type,
            )
            .order_by(Coach.id)
        )
        return result.scalars().all()


    async def find_all_train_on_journey_date(self,journey_date):
        result=await self.db.execute(
            select(TrainSchedule)
            .options(selectinload(TrainSchedule.train))
            .where(TrainSchedule.journey_date==journey_date)
        )
        return result.scalars().all()


    async def get_all_trains(self):
        result=await self.db.execute(select(Train))
        return result.scalars().all()

    async def find_journey_date(self,journey_date):
        result=await self.db.execute(
            select(TrainSchedule).where(TrainSchedule.journey_date==journey_date)
        )
        return result.scalar_one_or_none()


