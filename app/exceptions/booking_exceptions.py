from app.exceptions.ResourceNotFoundException import ResourceNotFoundException
from app.exceptions.InvalidOperationException import InvalidOperationException


class BookingNotFoundException(ResourceNotFoundException):
    pass


class BookingOperationException(InvalidOperationException):
    pass
