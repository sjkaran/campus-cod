"""Domain exceptions. Each maps to an HTTP status in app.main handlers."""


class AppError(Exception):
    status_code = 500
    default_detail = "Internal server error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class BadRequestError(AppError):
    status_code = 400
    default_detail = "Bad request"


class UnauthorizedError(AppError):
    status_code = 401
    default_detail = "Not authenticated"


class ForbiddenError(AppError):
    status_code = 403
    default_detail = "You do not have permission to perform this action"


class NotFoundError(AppError):
    status_code = 404
    default_detail = "Resource not found"


class ConflictError(AppError):
    status_code = 409
    default_detail = "Conflict"
