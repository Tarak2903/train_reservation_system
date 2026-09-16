from sqlalchemy import select

from app.models.schemas.train_schedule import TrainSchedule


class JourneyRepository:
    def __init__(self,db):
        self.db=db

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

    async def find_journey_date(self,journey_date):
        result=await self.db.execute(
            select(TrainSchedule).where(TrainSchedule.journey_date==journey_date)
        )
        return result.scalar_one_or_none()