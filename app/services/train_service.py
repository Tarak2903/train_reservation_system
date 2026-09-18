from datetime import date, timedelta

from dns import update
from sqlalchemy import select

from app.exceptions.resource_already_exists_exception import ResourceAlreadyExistsException
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
    def __init__(self, train_repo,journey_repo,coach_repo):
        self.train_repo = train_repo
        self.journey_repo=journey_repo
        self.coach_repo=coach_repo


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


    async def get_layout(self, train_id, class_type):
        train = await self.train_repo.find_train_by_id(train_id)
        if not train:
            raise TrainNotFoundException("Train doesnt exists")


        result= await self.coach_repo.get_coaches_by_train_id_and_class_type(train_id, class_type)
        if len(result)==0:
            raise ResourceNotFoundException("Coach doesnt exist with this class type")
        return result


    async def get_all_trains(self,journey_date):
        if journey_date is None:
            trains=await self.train_repo.get_all_trains()
            if not trains:
                raise TrainNotFoundException("No trains available")
            return  trains
        else:
            trains=await self.train_repo.find_all_train_on_journey_date(journey_date)
            if not trains:
                raise TrainNotFoundException("No trains available")
            return  trains



    async def find_train_by_number(self,train_number):
        trains=await self.train_repo.find_train_by_number(train_number)
        return trains


    async def update_train(self, train_id, train_request):
        train = await self.train_repo.find_train_by_id(train_id)

        if not train:
            raise ResourceNotFoundException("Train doesn't exist")

        update_data = train_request.model_dump(exclude_unset=True)
        print("Update_data",update_data)
        for key, value in update_data.items():
            setattr(train, key, value)

        await self.train_repo.db.commit()
        await self.train_repo.db.refresh(train)

        return train

