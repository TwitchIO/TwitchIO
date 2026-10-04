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
from typing import TYPE_CHECKING, Any, Self, Unpack

from .dispatcher import EventDispatcher
from .enums import TransportMethod
from .http import HTTPClient
from .utils import MISSING
from .websockets import WebsocketManager


if TYPE_CHECKING:
    from collections.abc import Callable

    from .eventsub import Subscription
    from .types_.clients import ClientOptionsT
    from .types_.eventsub import SubscriptionCreateRequest, SubscriptionResponseT


class Client:
    def __init__(self, **options: Unpack[ClientOptionsT]) -> None:
        self._client_id: str = options.get("client_id")
        self._client_secret: str | None = options.get("client_secret")
        self._dcf: bool = options.get("dcf", False)

        if not self._dcf and not self._client_secret:
            raise RuntimeError("Client must use a 'client_secret' when not set to 'dcf'.")

        session = options.get("session", MISSING)
        connector = options.get("connector", MISSING)

        self._http = HTTPClient(
            client_id=self._client_id,
            client_secret=self._client_secret,
            session=session,
            connector=connector,
            is_dcf=self._dcf,
        )
        self._events = EventDispatcher()
        self._sockets = WebsocketManager(self)

        self._raw_events = options.get("enable_raw_events", False)
        self.__stop_event = asyncio.Event()

    @property
    def dispatcher(self) -> EventDispatcher:
        return self._events

    @property
    def http(self) -> HTTPClient:
        return self._http

    def __repr__(self) -> str:
        return "Client()"

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self.close()

    async def start(self) -> None:
        await self.login()
        await self.__stop_event.wait()

    async def login(self) -> None:
        if self.__stop_event.is_set():
            raise RuntimeError(f"Cannot start {type(self).__name__} after it has been stopped.")

        if not self._http._has_setup:
            await self._http.setup()

        if not self._sockets._has_setup:
            await self._sockets.setup()

    def run(
        self,
        *,
        debug: bool | None = None,
        loop_factory: Callable[..., asyncio.AbstractEventLoop] | None = None,
    ) -> None:
        async def runner() -> None:
            async with self:
                await self.start()

        try:
            asyncio.run(runner(), debug=debug, loop_factory=loop_factory)
        except KeyboardInterrupt:
            pass

    async def close(self) -> None:
        if self.__stop_event.is_set():
            return

        await self._http.close()
        await self._sockets.shutdown()
        self._events.cleanup()

        self.__stop_event.set()

    async def _subscribe(
        self,
        subscription: Subscription[Any],
        *,
        transport: TransportMethod,
        session_id: str = MISSING,
        conduit_id: str = MISSING,
        callback: str = MISSING,
        secret: str = MISSING,
    ) -> SubscriptionResponseT:
        if transport is TransportMethod.WEBSOCKET:
            extras = {"session_id": session_id}
        elif transport is TransportMethod.CONDUIT:
            extras = {"conduit_id": conduit_id}
        elif transport is TransportMethod.WEBHOOK:
            extras = {"callback": callback, "secret": secret}

        data: SubscriptionCreateRequest = {**subscription._data, "transport": {"method": transport.value, **extras}}  # type: ignore
        return await self._http.create_eventsub_subscription(**data)

    async def raw_subscribe_websocket(self, subscription: Subscription[Any], *, session_id: str) -> SubscriptionResponseT:
        return await self._subscribe(
            subscription,
            transport=TransportMethod.WEBSOCKET,
            session_id=session_id,
        )

    async def raw_subscribe_webhook(
        self,
        subscription: Subscription[Any],
        *,
        callback: str,
        secret: str,
    ) -> SubscriptionResponseT:
        return await self._subscribe(
            subscription,
            transport=TransportMethod.WEBHOOK,
            callback=callback,
            secret=secret,
        )

    async def raw_subscribe_conduit(self, subscription: Subscription[Any], *, conduit_id: str) -> SubscriptionResponseT:
        return await self._subscribe(
            subscription,
            transport=TransportMethod.CONDUIT,
            conduit_id=conduit_id,
        )


class ManagedClient(Client):
    def __init__(self, **options: Unpack[ClientOptionsT]) -> None:
        if options.get("dcf"):
            raise RuntimeError("The 'dcf' option is not supported by ManagedClient.")

        super().__init__(**options)
