from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.InvalidOperationException import InvalidOperationException
from app.exceptions.UnauthenticatedException import UnauthenticatedException
from app.exceptions.ResourceNotFoundException import ResourceNotFoundException
from app.exceptions.ResrouceAlreadyExistsException import (
    ResourceAlreadyExistsException,
)
from app.exceptions.ForbiddenException import ForbiddenException

from app.models.DTOs.api_response import APIResponse, ErrorDetail


def error_response(status_code: int, message: str):
    return JSONResponse(
        status_code=status_code,
        content=APIResponse(
            success=False,
            message=message,
            data={},
            errors=[
                ErrorDetail(
                    code=status_code,
                    details=message,
                )
            ],
        ).model_dump(mode="json"),
    )


async def resource_already_exists_exception(
    request: Request,
    exc: ResourceAlreadyExistsException,
):
    return error_response(409, exc.message)


async def resource_doesnt_exists_exception(
    request: Request,
    exc: ResourceNotFoundException,
):
    return error_response(404, exc.message)


async def unauthenticated_exception(
    request: Request,
    exc: UnauthenticatedException,
):
    return error_response(401, exc.message)


async def forbidden_exception(
    request: Request,
    exc: ForbiddenException,
):
    return error_response(403, exc.message)


async def invalid_operation_exception(
    request: Request,
    exc: InvalidOperationException,
):
    return error_response(400, exc.message)

async def invalid_time_exception(
    request: Request,
    exc: ValueError,
):
    return error_response(422, "Arrival time should be smaller than departure time")


async def validation_exception(
    request: Request,
    exc: RequestValidationError,
):
    errors = []
    status_code = 422

    for error in exc.errors():
        field = ".".join(str(location) for location in error["loc"])

        if error["type"] == "json_invalid":
            error_code = 400
            status_code = 400

            errors.append(
                ErrorDetail(
                    code=error_code,
                    details="Invalid JSON sent in the request. Please check the JSON syntax, commas, brackets, quotes, etc.",
                )
            )

        elif error["type"] == "missing":
            error_code = 400
            status_code = 400

            errors.append(
                ErrorDetail(
                    code=error_code,
                    details=f"{field}: Required field is missing",
                )
            )

        else:
            error_code = 422

            errors.append(
                ErrorDetail(
                    code=error_code,
                    details=f"{field}: {error['msg']}",
                )
            )

    return JSONResponse(
        status_code=status_code,
        content=APIResponse(
            success=False,
            message=(
                "Bad request"
                if status_code == 400
                else "Validation error"
            ),
            data={},
            errors=errors,
        ).model_dump(mode="json"),
    )

