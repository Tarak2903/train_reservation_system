from fastapi import APIRouter, Depends
from starlette import status

from app.dependency import get_train_service
from app.auth import get_current_admin
from app.models.DTOs.APIResponse import APIResponse
from app.models.DTOs.Train.TrainCreationRequest import TrainCreationRequest
from app.models.DTOs.Train.TrainResponse import TrainResponse
from app.models.DTOs.Train.JourneyCreationRequest import JourneyCreationRequest
from app.models.DTOs.Train.JourneyResponse import JourneyResponse
from app.models.DTOs.Coach.CoachCreationRequest import CoachCreationRequest
from app.models.DTOs.Coach.CoachResponse import CoachResponse
from app.services.TrainService import TrainService

router = APIRouter(prefix="/admin")


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


@router.post("/trains/{train_id}/journeys",
             response_model=APIResponse[JourneyResponse],
             status_code=status.HTTP_201_CREATED, tags=["Admin"]
             )
async def add_train_journey(
    train_id: int,
    journey: JourneyCreationRequest,
    admin=Depends(get_current_admin),
    train_service: TrainService = Depends(get_train_service),
):
    created = await train_service.add_journey(train_id, journey)

    return APIResponse(
        success=True,
        message="Train journey added successfully",
        data=JourneyResponse(
            journey_id=created.id,
            train_id=created.train_id,
            journey_date=created.journey_date,
        ),
    )


@router.post("/trains/{train_id}/coaches",
             response_model=APIResponse[CoachResponse],
             status_code=status.HTTP_201_CREATED ,tags=["Admin"])
async def add_train_coach(
    train_id: int,
    coach: CoachCreationRequest,
    admin=Depends(get_current_admin),
    train_service: TrainService = Depends(get_train_service),
):
    created = await train_service.add_coach(train_id, coach)

    return APIResponse(
        success=True,
        message="Coach added successfully",
        data=CoachResponse(
            coach_number=created.coach_number,
            class_type=created.class_type.value,
            total_seat_capacity=created.total_seat_capacity,
            rac_capacity=created.rac_capacity,
        ),
    )

#
# @router.post("/coaches/{coach_id}/seats", response_model=APIResponse[list[SeatResponse]], tags=["Admin"])
# async def add_coach_seat(
#     coach_id: int,
#     seat: SeatCreationRequest,
#     admin=Depends(get_current_admin),
#     train_service: TrainService = Depends(get_train_service),
# ):
#     created = await train_service.add_seat(coach_id, seat.seat_count)
#
#     return APIResponse(
#         success=True,
#         message="Seats added successfully",
#         data=[
#             SeatResponse(
#                 seat_id=item.id,
#                 coach_id=item.coach_id,
#                 seat_number=item.seat_number,
#             )
#             for item in created
#         ],
#     )
