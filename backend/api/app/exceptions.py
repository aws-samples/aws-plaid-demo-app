from http import HTTPStatus

from aws_lambda_powertools.event_handler.exceptions import ServiceError


class ConflictError(ServiceError):
    """API Gateway and ALB Conflict Error (409)"""

    def __init__(self, msg: str):
        super().__init__(HTTPStatus.CONFLICT, msg)
