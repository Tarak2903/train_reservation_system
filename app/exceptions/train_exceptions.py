from app.exceptions.ResourceNotFoundException import ResourceNotFoundException
from app.exceptions.ResrouceAlreadyExistsException import ResourceAlreadyExistsException


class TrainNotFoundException(ResourceNotFoundException):
    pass


class TrainAlreadyExistsException(ResourceAlreadyExistsException):
    pass
