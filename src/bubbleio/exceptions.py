class BaseError(Exception):
    """
    Example:
        error_obj = {
            "error": {
                "code": "invalidRequest",
                "message": "Invalid hostname for this tenancy",
                "innerError": {
                    "request-id": "80fc571a-3262-404b-8a67-22f9cad99016",
                    "date": "2020-01-14T19:01:55"
                }
            }
        }
    """

    def __init__(self, msg, error_obj):
        if isinstance(error_obj, dict):
            Exception.__init__(self, msg + f' Error: {error_obj.get("body", {}).get("message")}')
        else:
            Exception.__init__(self, msg + f' Error: {str(error_obj)[:100].replace(chr(10)," ")}')


class UnknownError(BaseError):
    pass


class TokenRequired(BaseError):
    pass


class BadRequest(BaseError):
    pass


class Unauthorized(BaseError):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class Forbidden(BaseError):
    pass


class NotFound(BaseError):
    def __init__(self, endpoint: str, error_obj: any):
        error_message = 'Not found'
        if isinstance(error_obj, dict) and error_obj.get("body", {}).get("message"):
            error_message = error_obj['body']['message']
            if endpoint in error_message:
                Exception.__init__(self, f'Endpoint {endpoint} was not found, check Object name entry field')
                return
        Exception.__init__(self, f'Error when calling endpoint {endpoint} : {error_message}. Check API url entry')


class MethodNotAllowed(BaseError):
    pass


class NotAcceptable(BaseError):
    pass


class Conflict(BaseError):
    pass


class Gone(BaseError):
    pass


class LengthRequired(BaseError):
    pass


class PreconditionFailed(BaseError):
    pass


class RequestEntityTooLarge(BaseError):
    pass


class UnsupportedMediaType(BaseError):
    pass


class RequestedRangeNotSatisfiable(BaseError):
    pass


class UnprocessableEntity(BaseError):
    pass


class TooManyRequests(BaseError):
    pass


class InternalServerError(BaseError):
    pass


class NotImplemented(BaseError):
    pass


class ServiceUnavailable(BaseError):
    pass


class GatewayTimeout(BaseError):
    pass


class InsufficientStorage(BaseError):
    pass


class BandwidthLimitExceeded(BaseError):
    pass
