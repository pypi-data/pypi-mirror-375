class OrchError(Exception):
    pass


class Unauthorized(OrchError):
    pass


class Forbidden(OrchError):
    pass


class NotFound(OrchError):
    pass


class RateLimited(OrchError):
    pass


class ServerError(OrchError):
    pass

