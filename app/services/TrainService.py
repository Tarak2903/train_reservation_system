from datetime import date, timedelta

from dns import update
from sqlalchemy import select

from app.exceptions.ResrouceAlreadyExistsException import ResourceAlreadyExistsException
from app.exceptions.train_exceptions import (
    ResourceNotFoundException,
    TrainAlreadyExistsException,
    TrainNotFoundException,
)
from app.models.schemas.train import Train
from app.models.schemas.train_schedule import TrainSchedule
from app.models.schemas.coach import Coach
from app.models.schemas.seat import Seat


class TrainService:
    def __init__(self, train_repo,journey_repo):
        self.train_repo = train_repo
        self.journey_repo=journey_repo


    async def check_existing_train_by_number(self,train_request):
        if await self.train_repo.find_train_by_number(train_request.train_number):
            raise TrainAlreadyExistsException("Train already exists")


    async def add_train(self, train_request):
        await self.check_existing_train_by_number(train_request)

        train = Train(**train_request.model_dump())
        await self.train_repo.add_train(train)

        today = date.today()
        for i in range(7):
            await self.journey_repo.add_schedule(
                TrainSchedule(
                    train_id=train.id,
                    journey_date=today + timedelta(days=i),
                )
            )
        await self.train_repo.db.commit()
        await self.train_repo.db.refresh(train)
        return train


    async def get_layout(self, train_id, journey_date, class_type):
        train = await self.train_repo.find_train_by_id(train_id)
        if not train:
            raise TrainNotFoundException("Train doesnt exists")

        if not await self.train_repo.find_schedule(train_id, journey_date):
            raise TrainNotFoundException("Journey date is not available")

        return await self.train_repo.get_coaches(train_id, class_type)


    async def get_all_trains(self):
        trains=await self.train_repo.get_all_trains()
        if not trains:
            raise TrainNotFoundException("No trains available")
        return  trains


    async def get_coaches_by_train_number(self,train_number):
        train=await self.find_train_by_number(train_number)
        if not train :
            raise TrainNotFoundException("No trains exist with the following number ")

        coaches=await self.train_repo.get_coaches_by_train_number(train_number)

        if not coaches:
            raise ResourceNotFoundException("No coaches added in the train yet")
        return coaches.coaches


    async def find_train_by_number(self,train_number):
        trains=await self.train_repo.find_train_by_number(train_number)
        return trains

