from typing import Optional

import aiohttp


class ExpressipyException(Exception):
    """Base exception for Expressipy"""

    pass


class HTTPException(ExpressipyException):
    """Exception raised when an HTTP request fails"""

    def __init__(
        self, response: aiohttp.ClientResponse, message: Optional[str] = None
    ) -> None:
        self.response = response
        self.status = response.status
        self.reason = response.reason
        if message is None:
            message = f"HTTP {self.status} {self.reason}"
        super().__init__(message)


class NotFound(HTTPException):
    """Exception raised when a resource is not found (404)."""

    pass


class BadRequest(HTTPException):
    """Exception raised when a resource is not malformed (400)."""

    pass
