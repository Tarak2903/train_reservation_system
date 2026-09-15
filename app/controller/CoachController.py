from fastapi import APIRouter, Depends, Path
from starlette import status

from app.auth import get_current_admin
from app.dependency import get_train_service, get_coach_service
from app.models.DTOs.APIResponse import APIResponse
from app.models.DTOs.Coach.CoachCreationRequest import CoachCreationRequest
from app.models.DTOs.Coach.CoachResponse import CoachResponse
from app.services.CoachService import CoachService
from app.services.TrainService import TrainService

router=APIRouter()

@router.get('/trains/{train_number}/coaches',response_model=APIResponse[list[CoachResponse]],tags=['Booking'])
async def get_coaches_by_train_number(train_number:int=Path(),coach_service:CoachService=Depends(get_coach_service)):
    coaches= await coach_service.get_coaches_by_train_number(train_number)

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


@router.post("/trains/{train_id}/coaches",
             response_model=APIResponse[CoachResponse],
             status_code=status.HTTP_201_CREATED ,tags=["Admin"])
async def add_train_coach(
    coach: CoachCreationRequest,
    train_id: int=Path(),
    admin=Depends(get_current_admin),
    coach_service: CoachService = Depends(get_coach_service),
):
    created = await coach_service.add_coach(train_id, coach)

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