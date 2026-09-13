from app.exceptions.ResourceNotFoundException import ResourceNotFoundException
from app.exceptions.ResrouceAlreadyExistsException import ResourceAlreadyExistsException
from app.exceptions.train_exceptions import TrainNotFoundException
from app.models.schemas.coach import Coach
from app.models.schemas.seat import Seat


class CoachService:
    def __init__(self,coach_repo,train_repo,seat_repo):
        self.coach_repo=coach_repo
        self.train_repo=train_repo
        self.seat_repo=seat_repo


    async def validate_train_by_id(self,train_id):
        train = await self.train_repo.find_train_by_id(train_id)
        if not train:
            raise ResourceNotFoundException("Train doesnt exists")
        return train


    async def validate_train_by_number(self,train_number):
        train = await self.train_repo.find_train_by_number(train_number)
        if not train:
            raise TrainNotFoundException("No trains exist with the following number ")

    async def add_coach(self, train_id, coach_request):
        await self.validate_train_by_id(train_id)
        result=await self.coach_repo.find_coach_by_coach_number_and_train_id(train_id,coach_request.coach_number)

        if result is not None:
            raise ResourceAlreadyExistsException("Coach already exists")

        coach = Coach(
            train_id=train_id,
            coach_number=coach_request.coach_number,
            class_type=coach_request.class_type,
            total_seat_capacity=coach_request.total_seat_capacity,
            rac_capacity=coach_request.rac_capacity,
        )
        await self.coach_repo.add_coach(coach)

        await self.add_seat(
            coach.id,
            coach_request.total_seat_capacity,
        )
        await self.train_repo.db.commit()
        await self.train_repo.db.refresh(coach)
        return coach


    async def add_seat(self, coach_id, seat_count):
        coach = await self.train_repo.find_coach(coach_id)
        if not coach:
            raise ResourceNotFoundException("Coach doesnt exists")
        last_seat_number = 0
        seats = [
            Seat(
                coach_id=coach_id,
                seat_number=last_seat_number + i,
            )
            for i in range(1, seat_count + 1)
        ]
        await self.seat_repo.add_seat(seats)
        return seats


    async def get_coaches_by_train_number(self,train_number):
        await self.validate_train_by_number(train_number)
        coaches=await self.coach_repo.get_coaches_by_train_number(train_number)
        if not coaches:
            raise ResourceNotFoundException("No coaches added in the train yet")
        return coaches.coaches
