from fastapi import APIRouter, Depends

from app.dependency import get_train_service
from app.models.DTOs.APIResponse import APIResponse
from app.models.DTOs.Coach.CoachResponse import CoachResponse
from app.models.DTOs.Train.TrainResponse import TrainResponse
from app.services.TrainService import TrainService

router=APIRouter()


@router.get('/trains',response_model=APIResponse[list[TrainResponse]])
async def get_all_trains(train_service:TrainService=Depends(get_train_service)):
    trains=await train_service.get_all_trains()

    return APIResponse(
        success=True,
        message='Trains fetched successfully',
        data=[

             TrainResponse(
                train_number=train.train_number,
               train_name=train.train_name,
               departure_time=train.departure_time,
               arrival_time=train.arrival_time,
               source=train.source,
                destination=train.destination
    )
            for train in trains

        ]
    )
@router.get('/trains/train_number',response_model=APIResponse[list[CoachResponse]])
async def get_coaches_by_train_number(train_number,train_service:TrainService=Depends(get_train_service)):

    coaches= await train_service.get_coaches_by_train_number(train_number)

    return APIResponse(
        success=True,
        message='Coaches fetched successfully',
        data=
        [
            CoachResponse(
                coach_number=coach.coach_number,
                class_type=coach.class_type,
                total_seat_capacity=coach.total_seat_capacity,
                rac_capacity=coach.rac_capacity
            )
            for coach in coaches
        ]
    )