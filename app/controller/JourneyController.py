from fastapi import APIRouter, Depends
from starlette import status
from app.auth import get_current_admin
from app.dependency import get_train_service, get_journey_service
from app.models.DTOs.APIResponse import APIResponse
from app.models.DTOs.Train.JourneyCreationRequest import JourneyCreationRequest
from app.models.DTOs.Train.JourneyResponse import JourneyResponse
from app.services.JourneyService import JourneyService

router=APIRouter()

@router.post("/trains/{train_id}/journeys",
             response_model=APIResponse[JourneyResponse],
             status_code=status.HTTP_201_CREATED, tags=["Admin"]
             )
async def add_train_journey(
    train_id: int,
    journey: JourneyCreationRequest,
    admin=Depends(get_current_admin),
    journey_service: JourneyService = Depends(get_journey_service),
):
    created = await journey_service.add_journey(train_id, journey)

    return APIResponse(
        success=True,
        message="Train journey added successfully",
        data=JourneyResponse(
            journey_id=created.id,
            train_id=created.train_id,
            journey_date=created.journey_date,
        ),
    )
