"""MIT License

Copyright (c) 2025 - Present Evie. P., Chillymosh and TwitchIO

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__all__ = (
    "BadRequestError",
    "ForbiddenError",
    "HTTPException",
    "MissingCLIParamError",
    "MissingConditionError",
    "MissingTokenError",
    "NotFoundError",
    "RatelimitOverflowError",
    "RatelimitedError",
    "SubscriptionException",
    "TwitchIOException",
    "TwitchServerError",
    "UnauthorizedError",
    "WebsocketConnectionError",
    "WebsocketException",
)

# TODO: Docs...


class TwitchIOException(Exception): ...


# HTTP
class HTTPException(TwitchIOException): ...


class TwitchServerError(HTTPException): ...


class MissingTokenError(HTTPException): ...


class UnauthorizedError(HTTPException): ...


class ForbiddenError(HTTPException): ...


class NotFoundError(HTTPException): ...


class BadRequestError(HTTPException): ...


# Ratelimits
class RatelimitedError(HTTPException): ...


class RatelimitOverflowError(TwitchIOException):
    def __init__(self, waiters: int, limit: int) -> None:
        super().__init__(f"Ratelimited (slow down): ({waiters}) requests are currently waiting [max: {limit}]")
        self.waiters = waiters
        self.limit = limit


# ...
class MissingCLIParamError(TwitchIOException): ...


class WebsocketException(TwitchIOException): ...


class WebsocketConnectionError(WebsocketException): ...


class SubscriptionException(TwitchIOException): ...


class MissingConditionError(SubscriptionException): ...
