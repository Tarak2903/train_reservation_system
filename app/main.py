from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.exceptions.invalid_operation_exception import InvalidOperationException
from app.exceptions.resource_not_found_execption import ResourceNotFoundException
from app.exceptions.resource_already_exists_exception import ResourceAlreadyExistsException
from app.exceptions.unauthenticated_exception import UnauthenticatedException
from app.exceptions.forbidden_exception import ForbiddenException
from app.exceptions.handler import (
    resource_already_exists_exception,
    resource_doesnt_exists_exception,
    unauthenticated_exception,
    forbidden_exception,
    invalid_operation_exception,
    validation_exception, invalid_time_exception,
)
from app.controller.AuthController import router as auth_router
from app.controller.BookingController import router as booking_router
from app.controller.TrainController import router as train_router
from app.controller.CoachController import router as coach_router
from app.controller.JourneyController import router as journey_router
from app.helpers.database import Base, engine


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def register_exception_handlers(app: FastAPI) -> None:
    handlers = [(ResourceAlreadyExistsException, resource_already_exists_exception),
        (ResourceNotFoundException, resource_doesnt_exists_exception),(UnauthenticatedException, unauthenticated_exception),
        (ForbiddenException, forbidden_exception),(InvalidOperationException, invalid_operation_exception),
        (RequestValidationError, validation_exception),(ValueError, invalid_time_exception)]

    for exception, handler in handlers:
        app.add_exception_handler(exception, handler)

def register_routers(app: FastAPI) -> None:
    routers = [auth_router,booking_router,train_router,coach_router,journey_router,]
    for router in routers:
        app.include_router(router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    yield
    await engine.dispose()



app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)
register_routers(app)




