from app.exceptions.resource_not_found_execption import ResourceNotFoundException
from app.exceptions.resource_already_exists_exception import ResourceAlreadyExistsException


class TrainNotFoundException(ResourceNotFoundException):
    pass


class TrainAlreadyExistsException(ResourceAlreadyExistsException):
    pass
