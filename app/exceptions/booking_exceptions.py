from app.exceptions.resource_not_found_execption import ResourceNotFoundException
from app.exceptions.invalid_operation_exception import InvalidOperationException


class BookingNotFoundException(ResourceNotFoundException):
    pass


class BookingOperationException(InvalidOperationException):
    pass
