from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.exceptions.InvalidOperationException import InvalidOperationException
from app.exceptions.ResourceNotFoundException import ResourceNotFoundException
from app.exceptions.ResrouceAlreadyExistsException import ResourceAlreadyExistsException
from app.exceptions.UnauthenticatedException import UnauthenticatedException
from app.exceptions.ForbiddenException import ForbiddenException
from app.exceptions.handler import (
    resource_already_exists_exception,
    resource_doesnt_exists_exception,
    unauthenticated_exception,
    forbidden_exception,
    invalid_operation_exception,
    http_exception,
    validation_exception,
)
from app.helpers.database import Base, engine


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    yield
    await engine.dispose()


from app.controller.AuthController import router as auth_router
from app.controller.BookingController import router as booking_router
from app.controller.TrainController import router as train_router
from app.controller.CoachController import router as coach_router
app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(booking_router)
app.include_router(train_router)
app.include_router(coach_router)

app.add_exception_handler(
    ResourceAlreadyExistsException,
    resource_already_exists_exception,
)
app.add_exception_handler(
    ResourceNotFoundException,
    resource_doesnt_exists_exception,
)
app.add_exception_handler(
    UnauthenticatedException,
    unauthenticated_exception,
)
app.add_exception_handler(
    ForbiddenException,
    forbidden_exception,
)
app.add_exception_handler(
    InvalidOperationException,
    invalid_operation_exception,
)
app.add_exception_handler(HTTPException, http_exception)
app.add_exception_handler(RequestValidationError, validation_exception)


@app.get("/")
async def root():
    return {"message": "Train Reservation System"}
