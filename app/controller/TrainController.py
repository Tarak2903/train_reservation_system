from datetime import date

from fastapi import APIRouter, Depends, Path, Query
from starlette import status

from app.auth import get_current_admin, get_current_user
from app.dependency import get_train_service
from app.models.DTOs.APIResponse import APIResponse
from app.models.DTOs.Train.TrainCreationRequest import TrainCreationRequest
from app.models.DTOs.Train.TrainResponse import TrainResponse
from app.models.DTOs.Train.TrainUpdateRequest import TrainUpdateRequest
from app.models.enums import CoachClass
from app.models.schemas.user import User
from app.services.TrainService import TrainService

router=APIRouter()


@router.get('/trains',response_model=APIResponse[list[TrainResponse]],tags=['Booking'])
async def get_all_trains(journey_date:date=Query(default=None),train_service:TrainService=Depends(get_train_service)):
    result=await train_service.get_all_trains(journey_date)
    if journey_date is None:
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
                for train in result

            ]
        )
    return APIResponse(
        success=True,
        message='Trains fetched successfully',
        data=[

             TrainResponse(
                train_number=train.train.train_number,
               train_name=train.train.train_name,
               departure_time=train.train.departure_time,
               arrival_time=train.train.arrival_time,
               source=train.train.source,
                destination=train.train.destination
    )
            for train in result

        ]
    )

@router.post("/trains",
             response_model=APIResponse[TrainResponse],
             status_code=status.HTTP_201_CREATED , tags=["Admin"])
async def add_train(
    train: TrainCreationRequest,
    admin=Depends(get_current_admin),
    train_service: TrainService = Depends(get_train_service),
):
    created_train = await train_service.add_train(train)

    return APIResponse(
        success=True,
        message="Train created successfully",
        data=TrainResponse(
            train_number=created_train.train_number,
            train_name=created_train.train_name,
            source=created_train.source,
            destination=created_train.destination,
            departure_time=created_train.departure_time,
            arrival_time=created_train.arrival_time,
        ),
    )

@router.get("/trains/{train_id}/layout", response_model=APIResponse[list], tags=["Booking"])
async def get_seat_layout(
    train_id: int=Path(),
    journey_date: date=Query(),
    class_type: CoachClass=Query(),
    current_user: User = Depends(get_current_user),
    train_service: TrainService = Depends(get_train_service),
):
    coaches = await train_service.get_layout(train_id, journey_date, class_type)

    data = [
        {
            "coach_id": coach.id,
            "coach_number": coach.coach_number,
            "class_type": coach.class_type.value,
            "seats": [
                {
                    "seat_id": seat.id,
                    "seat_number": seat.seat_number,
                }
                for seat in coach.seats
            ],
        }
        for coach in coaches
    ]

    return APIResponse(
        success=True,
        message="Seat layout retrieved successfully",
        data=data,
    )

@router.patch("/trains/{train_id}",response_model=APIResponse[TrainResponse],tags=["Admin"],)
async def update_train(train_request: TrainUpdateRequest,train_id: int = Path(gt=0),
    admin=Depends(get_current_admin),train_service: TrainService = Depends(get_train_service),):

    updated_train = await train_service.update_train(train_id,train_request,)
    return APIResponse(
        success=True,
        message="Train updated successfully",
        data=TrainResponse(
            train_number=updated_train.train_number,
            train_name=updated_train.train_name,
            source=updated_train.source,
            destination=updated_train.destination,
            departure_time=updated_train.departure_time,
            arrival_time=updated_train.arrival_time,
        ),
    )
