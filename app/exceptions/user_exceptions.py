from app.exceptions.ResourceNotFoundException import ResourceNotFoundException
from app.exceptions.ResrouceAlreadyExistsException import ResourceAlreadyExistsException


class UserAlreadyExistsException(ResourceAlreadyExistsException):
    pass


class UserDoesntExistsException(ResourceNotFoundException):
    pass
