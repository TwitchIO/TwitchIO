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
import urllib.parse
from typing import TYPE_CHECKING, Any, ClassVar, Unpack

from ..exceptions import *
from ..utils import MISSING


if TYPE_CHECKING:
    from aiohttp import ClientResponse

    from ..types_.http import APIRequestKwargs, HTTPMethodT, ParamMappingT
    from .clients import HTTPClient


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
        "_url",
        "could_404",
        "data",
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
        **kwargs: Unpack[APIRequestKwargs],
    ) -> None:
        self.params: ParamMappingT = kwargs.pop("params", {})
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

    def __str__(self) -> str:
        return str(self._url)

    def __repr__(self) -> str:
        return f"{self.method}[{self.base_url}]"

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

            if isinstance(value, (str, int)):
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

    def update_params(self, params: ParamMappingT, *, remove_none: bool = True) -> str:
        self.params.update(params)
        self._url = self.build_url(remove_none=remove_none)

        return self.url

    def update_headers(self, headers: dict[str, str]) -> None:
        self.headers.update(headers)

    def clear_auth(self) -> None:
        self.headers.pop("Authorization", "")


class RequestManager:
    def __init__(self, client: HTTPClient, /, app_token: str = MISSING, prefers_user: bool = False) -> None:
        self._client = client
        self._app_token = app_token
        self._prefers_user = prefers_user
        self._tokens: dict[str, str] = {}

    async def close(self) -> None: ...

    async def handle_error_code(self, route: Route, resp: ClientResponse, status: int) -> None:
        if status == 503:
            await asyncio.sleep(3)

        elif status == 400:
            raise BadRequestError  # TODO

        elif status == 429:
            if not await self.handle_ratelimits(route):
                raise HTTPException  # TODO

        elif status == 401 and not await self.handle_auth_error(route):
            raise UnauthorizedError  # TODO ...

        elif status == 404:
            if route.could_404:
                raise NotFoundError  # TODO ...

            raise HTTPException  # TODO ...

        raise HTTPException  # TODO: ...

    async def handle_ratelimits(self, route: Route, /) -> bool: ...

    async def handle_auth_error(self, route: Route, /) -> bool: ...

    def update_route(self, route: Route, /, extras: dict[str, Any]) -> None:
        headers = extras
        token: str | None = headers.get("Authorization")
        no_app = route.no_app

        if route.token_for and not token:
            token = self._tokens.get(route.token_for, self._app_token)

        elif no_app or self._prefers_user:
            moderator = route.params.get("moderator_id", "")
            broadcaster = route.params.get("broadcaster_id", "")

            token = self._tokens.get(moderator) if moderator else self._tokens.get(broadcaster)

        if not token and not no_app:
            token = self._app_token

        if not token or token is MISSING:
            raise MissingTokenError("No valid token available for this request.")

        headers.update({"Authorization": f"Bearer {token}"})
        route.update_headers(headers)
