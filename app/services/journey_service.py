from app.exceptions.ResourceNotFoundException import ResourceNotFoundException
from app.exceptions.ResrouceAlreadyExistsException import ResourceAlreadyExistsException
from app.models.schemas.train_schedule import TrainSchedule


class JourneyService:
    def __init__(self,journey_repo,train_repo):
        self.journey_repo=journey_repo
        self.train_repo=train_repo

    async def validate_train_by_id(self,train_id):
        if not await self.train_repo.find_train_by_id(train_id):
            raise ResourceNotFoundException("Train doesnt exists")


    async def validate_journey_date(self,train_id,journey_request):
        if await self.journey_repo.find_schedule(train_id,journey_request.journey_date,):
            raise ResourceAlreadyExistsException("Journey date already exists")


    async def add_journey(self, train_id, journey_request):
        await self.validate_train_by_id(train_id)
        await self.validate_journey_date(train_id,journey_request)
        journey = TrainSchedule(
            train_id=train_id,
            journey_date=journey_request.journey_date,
        )
        await self.journey_repo.add_schedule(journey)
        await self.journey_repo.db.commit()
        await self.journey_repo.db.refresh(journey)
        return journey