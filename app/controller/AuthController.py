from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.dependency import get_auth_service
from app.models.DTOs.api_response import APIResponse
from app.models.DTOs.Auth.signup_request import SignupRequest
from app.models.DTOs.Auth.token import Token
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth")


@router.post("/signup", response_model=APIResponse[dict],status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def signup_user(
    user: SignupRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    created_user = await auth_service.signup_user(user)

    return APIResponse(
        success=True,
        message="User created successfully",
        data={
            "user_id": created_user.id,
            "user_name": created_user.user_name,
            "role": created_user.role.value,
        },
    )


@router.post("/login", response_model=APIResponse[Token], tags=["Authentication"])
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    token = await auth_service.login_user(form_data)

    return APIResponse(
        success=True,
        message="Login successful",
        data=Token(
            access_token=token,
            token_type="bearer",
        ),
    )


@router.post("/token", response_model=Token, include_in_schema=False)
async def swagger_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    token = await auth_service.login_user(form_data)

    return Token(
        access_token=token,
        token_type="bearer",
    )
