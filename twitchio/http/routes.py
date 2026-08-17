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

from __future__ import annotations

import asyncio
import copy
import dataclasses
import time
import urllib.parse
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Unpack

from ..exceptions import *


if TYPE_CHECKING:
    from collections.abc import Mapping

    from aiohttp import ClientResponse

    from ..types_.http import APIRequestKwargs, HTTPMethodT, ParamMappingInputT, ParamMappingT
    from .clients import HTTPClient


# Twitch Global Ratelimits (per token?)
RL_RATE: float = 800.0
RL_PER: float = 60.0
REQUEST_RETRIES: int = 3


class Route:
    """Route class used by TwitchIO to prepare HTTP requests to Twitch.

    .. warning::

        You should not change or instantiate this class manually, as it is used internally.

    Attributes
    ----------
    params: dict[str, Any]
        A mapping of parameters used in the request.
    json: dict[Any, Any]
        The JSON used in the body of the request. Could be an empty :class:`dict`.
    headers: dict[str, str]
        The headers used in the request.
    token_for: str
        The User ID that was used to gather a token for authentication. Could be an empty :class:`str`.
    method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD', 'CONNECT', 'TRACE']
        The request method used.
    path: str
        The API endpoint requested.
    """

    __slots__ = (
        "_base_url",
        "_retries",
        "_url",
        "cost",
        "could_404",
        "data",
        "encoded",
        "headers",
        "json",
        "method",
        "no_app",
        "packed",
        "params",
        "path",
        "token_for",
        "use_id",
    )

    BASE: ClassVar[str] = "https://api.twitch.tv/helix/"
    ID_BASE: ClassVar[str] = "https://id.twitch.tv/"

    def __init__(
        self,
        method: HTTPMethodT,
        path: str,
        *,
        use_id: bool = False,
        no_app: bool = False,
        could_404: bool = False,
        encoded: bool = False,
        cost: int = 1,
        **kwargs: Unpack[APIRequestKwargs],
    ) -> None:
        self.params: ParamMappingT = dict(kwargs.pop("params", {}))
        self.json: Any = kwargs.get("json", {})
        self.headers: dict[str, str] = kwargs.get("headers", {})
        self.token_for: str = str(kwargs.get("token_for", ""))
        self.no_app = no_app
        self.could_404 = could_404
        self.use_id = use_id
        self.method = method
        self.path = path

        self._base_url: str = ""
        self._url: str = self.build_url(duplicate_key=not use_id)

        self.encoded = encoded
        if encoded:
            self.headers.update({"Content-Type": "application/x-www-form-urlencoded"})

        self._retries: int = REQUEST_RETRIES
        self.cost = cost

    def __str__(self) -> str:
        return str(self._url)

    # type: ignore[arg-type]
    def __repr__(self) -> str:
        return f"Route<{self.method}[{self.base_url}]>"

    def update_retries(self) -> int | None:
        if self._retries <= 0:
            return None

        self._retries -= 1
        return 1 + (self._retries * 2)

    def build_url(self, *, remove_none: bool = True, duplicate_key: bool = True) -> str:
        base = self.ID_BASE if self.use_id else self.BASE
        self.path = self.path.lstrip("/").rstrip("/")

        url: str = f"{base}{self.path}"
        self._base_url = url

        if not self.params:
            return url

        url += "?"

        # We expect a dict so keys should be unique...
        for key, value in copy.copy(self.params).items():
            if value is None:
                if remove_none:
                    del self.params[key]
                continue

            if isinstance(value, str | int):
                url += f"{key}={self.encode(str(value), safe='+', plus=True)}&"
            elif duplicate_key:
                for v in value:
                    url += f"{key}={self.encode(str(v), safe='+', plus=True)}&"
            else:
                joined: str = "+".join([self.encode(str(v), safe="+") for v in value])
                url += f"{key}={joined}&"

        return url.rstrip("&")

    @classmethod
    def encode(cls, value: str, /, safe: str = "", plus: bool = False) -> str:
        method = urllib.parse.quote_plus if plus else urllib.parse.quote
        unquote = urllib.parse.unquote_plus if plus else urllib.parse.unquote

        return method(value, safe=safe) if unquote(value) == value else value

    @property
    def url(self) -> str:
        """Property returning the URL used to make a request. Could include query parameters."""
        return self._url

    @property
    def base_url(self) -> str:
        """Property returning the URL used to make a request without query parameters."""
        return self._base_url

    def update_params(self, params: ParamMappingInputT, *, remove_none: bool = True) -> str:
        self.params.update(params)
        self._url = self.build_url(remove_none=remove_none)

        return self.url

    def update_headers(self, headers: dict[str, str]) -> None:
        self.headers.update(headers)

    def clear_auth(self) -> None:
        self.headers.pop("Authorization", "")


class Ratelimiter:
    def __init__(
        self,
        *,
        rate: float = RL_RATE,
        per: float = RL_PER,
        max_waiters: int = 26,
        burst: float | None = None,  # ~90-95% is safer but 100% (800) allows greater burst throughput...
    ) -> None:
        if rate <= 0 or per <= 0:
            raise ValueError("The 'rate' and 'per' parameters must be > 0.")

        self._per = per
        self._capacity = float(burst if burst is not None else rate)
        self._rate = rate / per

        self._tokens = self._capacity
        self._updated = time.monotonic()

        self._lock = asyncio.Lock()
        self._waiters = 0
        self._max_waiters = max_waiters

    @property
    def waiting(self) -> int:
        return self._waiters

    @property
    def tokens(self) -> float:
        elapsed = time.monotonic() - self._updated
        return min(self._capacity, self._tokens + elapsed * self._rate)

    async def acquire(self, cost: float = 1.0) -> None:
        if cost > self._capacity:
            raise ValueError(f"Cost to request is too high: Exceeds ratelimit capacity of {self._capacity}.")

        if self._waiters >= self._max_waiters:
            raise RatelimitOverflowError(self._waiters, self._max_waiters)

        self._waiters += 1
        try:
            async with self._lock:
                self._refill()

                deficit = cost - self._tokens

                if deficit > 0:
                    await asyncio.sleep(deficit / self._rate)
                    self._refill()

                self._tokens -= cost
        finally:
            self._waiters -= 1

    def update(self, headers: Mapping[str, str]) -> None:
        remaining = self._as_float(headers, "Ratelimit-Remaining")
        if remaining is None:
            return

        limit = self._as_float(headers, "Ratelimit-Limit")
        if limit and limit > 0 and limit != self._capacity:
            self._capacity = limit
            self._rate = limit / self._per

        reset = self._as_float(headers, "Ratelimit-Reset")
        self._refill()

        if remaining <= 0 and reset is not None:
            delay = max(0.0, reset - time.time())

            self._tokens = min(self._tokens, -delay * self._rate)
        else:
            self._tokens = min(self._tokens, remaining)

    def _refill(self) -> None:
        now = time.monotonic()

        self._tokens = min(self._capacity, self._tokens + (now - self._updated) * self._rate)
        self._updated = now

    def _as_float(self, headers: Mapping[str, str], name: str) -> float | None:
        value = headers.get(name) or headers.get(name.lower())

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None


@dataclasses.dataclass(slots=True)
class TokenContainer:
    bucket: Ratelimiter
    token: str
    refresh: str | None = None
    expires: int | None = None
    identity: Literal["app", "user"] = "user"
    user_id: str | None = None

    def __str__(self) -> str:
        return self.token

    def __int__(self) -> int:
        return self.expires if self.expires is not None else -1


class RequestManager:
    def __init__(self, client: HTTPClient, /, app_token: str, prefers_user: bool = False) -> None:
        self._client = client
        self._app_token = TokenContainer(bucket=Ratelimiter(burst=760), token=app_token, identity="app")
        self._prefers_user = prefers_user
        self._tokens: dict[str, TokenContainer] = {}

    async def close(self) -> None: ...

    async def handle_error_code(self, route: Route, /, *, resp: ClientResponse, status: int) -> int:
        # Twitch Server/CF/Gateway Error
        # NOTE: Twitch recommends (1) retry on 503; but doesn't actually hurt in cases of multiple errors...
        # Retrying on all other 5xx really doesn't cost either and prevents unneeded errors from blips...
        if status >= 500:
            sleep = route.update_retries()

            if sleep is None:
                if status == 500:
                    raise TwitchServerError  # TODO: ...

                raise HTTPException  # TODO: ...

            return sleep

        # We can't really handle this case; raise a specific error...
        elif status == 400:
            raise BadRequestError  # TODO

        # If we get this it means the bucket has failed also...
        elif status == 429:
            raise RatelimitedError  # TODO: ...

        # Best case token is expired and successfully refreshed...
        # Worst case token is invalid/can't be refreshed and we re-raise
        elif status == 401 and not await self.handle_auth_error(route):
            raise UnauthorizedError  # TODO ...

        # Token is not able to access the resource...
        elif status == 403:
            raise ForbiddenError  # TODO: ...

        # Some Twitch endpoints specifically return 404 for not found resources
        # We can handle this by telling the route should return 404...
        elif status == 404:
            if route.could_404:
                raise NotFoundError  # TODO ...

            raise HTTPException  # TODO ...

        # Anything not covererd in this handler is generic...
        raise HTTPException  # TODO: ...

    async def handle_ratelimits(self, route: Route, /, *, resp: ClientResponse) -> bool: ...

    async def handle_auth_error(self, route: Route, /) -> bool: ...

    def update_route(self, route: Route, /, extras: dict[str, Any]) -> TokenContainer | None:
        container: TokenContainer | None = None
        headers = extras
        token: str | None = headers.get("Authorization")
        no_app = route.no_app

        if route.token_for and not token:
            container = self._tokens.get(route.token_for, self._app_token)

        elif no_app or self._prefers_user:
            moderator = route.params.get("moderator_id", "")
            broadcaster = route.params.get("broadcaster_id", "")

            container = self._tokens.get(moderator) if moderator else self._tokens.get(broadcaster)

        if not container and not no_app:
            container = self._app_token

        if not container:
            raise MissingTokenError("No valid token available for this request.")

        headers["Authorization"] = f"Bearer {container.token}"
        route.update_headers(headers)
        return container
