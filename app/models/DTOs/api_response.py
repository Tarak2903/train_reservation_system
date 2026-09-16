from typing import Generic, TypeVar
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: int
    details: str


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None
    errors: list[ErrorDetail] = Field(default_factory=list)
