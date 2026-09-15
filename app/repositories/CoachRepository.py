from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.schemas.coach import Coach
from app.models.schemas.train import Train


class CoachRepository:
    def __init__(self,db:AsyncSession):
        self.db=db


    async def find_coach_by_coach_number_and_train_id(self,train_id,coach_number):
        result = await self.db.execute(
            select(Coach).where(
                Coach.train_id == train_id,
                Coach.coach_number == coach_number,
            )
        )
        return result.scalar_one_or_none()


    async def get_coaches_by_train_number(self, train_number):
        result = await self.db.execute(
            select(Train)
            .options(selectinload(Train.coaches))
            .where(Train.train_number == train_number)
        )
        return result.scalar_one_or_none()

    async def get_coaches_by_train_id_and_class_type(self,train_id,class_type):
        result=await self.db.execute(
        select(Coach)
        .options(selectinload(Coach.seats))
        .where(Coach.train_id==train_id,Coach.class_type==class_type)
        )
        return result.scalars().all()

    async def add_coach(self, coach):
        self.db.add(coach)
        await self.db.flush()
        return coach

    async def find_coach_by_id(self, coach_id):
        result = await self.db.execute(
            select(Coach).where(Coach.id == coach_id)
        )
        return result.scalar_one_or_none()