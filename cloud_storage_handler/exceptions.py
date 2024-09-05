"""ELIXIR's Cloud Storage Handler exceptions."""

from http import HTTPStatus

from werkzeug.exceptions import BadRequest, InternalServerError, NotFound


class ConfigNotFoundError(FileNotFoundError):
    """Configuration file not found error."""


exceptions = {
    Exception: {
        "message": "An unexpected error occurred. Please try again.",
        "code": HTTPStatus.INTERNAL_SERVER_ERROR,  # 500
    },
    BadRequest: {
        "message": "Invalid request. Please check your input and try again.",
        "code": HTTPStatus.BAD_REQUEST,  # 400
    },
    NotFound: {
        "message": "The requested resource could not be found.",
        "code": HTTPStatus.NOT_FOUND,  # 404
    },
    InternalServerError: {
        "message": "An internal server error occurred in the cloud storage handler",
        "code": HTTPStatus.INTERNAL_SERVER_ERROR,  # 500
    },
}
