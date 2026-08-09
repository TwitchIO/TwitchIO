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
import dataclasses
import logging
import time
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Self, cast

from picows import (
    WSCloseCode,
    WSFrame,
    WSListener,
    WSMsgType,
    WSTransport,
    ws_connect,  # type: ignore
)

from .exceptions import WebsocketException
from .utils import JSON_LOADS, MISSING


if TYPE_CHECKING:
    from twitchio.types_.eventsub import (
        MessageTypes,
        MetaData,
        NotificationMessage,
        ReconnectMessage,
        RevocationMessage,
        WelcomeMessage,
    )

    from .clients import Client


__all__ = ("WebsocketManager",)


LOGGER: logging.Logger = logging.getLogger(__name__)

WSS_URL: str = "wss://eventsub.wss.twitch.tv/ws"
MIN_KEEP_ALIVE: int = 10
MAX_KEEP_ALIVE: int = 600
CLEANUP_TIMEOUT: int = 5

FAIL_CODES: tuple[int | WSCloseCode, ...] = (
    WSCloseCode.PROTOCOL_ERROR,
    WSCloseCode.POLICY_VIOLATION,
    4001,
    4002,
    4003,
)
SOFT_FAIL_CODES: tuple[WSCloseCode, ...] = (
    WSCloseCode.NO_INFO,
    WSCloseCode.MESSAGE_TOO_BIG,
    WSCloseCode.INTERNAL_ERROR,
    WSCloseCode.SERVICE_RESTART,
    WSCloseCode.TRY_AGAIN_LATER,
)


@dataclasses.dataclass(slots=True)
class WSContainer:
    transport: WSTransport | None
    listener: WebsocketFrame | None
    manager: WebsocketManager


class WebsocketManager:
    def __init__(self, client: Client, /, *, keepalive_timeout: float = MIN_KEEP_ALIVE) -> None:
        self._client = client
        self._sockets: dict[str, Websocket] = {}
        self._tasks: set[asyncio.Task[None]] = set()
        self._keepalive = int(min(max(keepalive_timeout, MIN_KEEP_ALIVE), MAX_KEEP_ALIVE))

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self.shutdown()

    @property
    def sockets(self) -> MappingProxyType[str, Websocket]:
        return MappingProxyType(self._sockets)

    def get_socket(self, session_id: str, /) -> Websocket | None:
        return self._sockets.get(session_id)

    async def _handle_reconnect(self, socket: Websocket, listener: WebsocketFrame, *, error: Exception | None) -> None:
        if socket._closing or listener._close_expected or listener is not socket.listener:
            return

        code = listener._close_code
        reason = listener._close_reason

        if code is None:
            LOGGER.warning("%r received an unknown close code (%s: %s). Attempting to reconnect...", socket, error, code)
            await self.reconnect_socket(socket)
            return

        if code in FAIL_CODES:
            LOGGER.error("%r was disconnected forcefully by Twitch. Cannot reconnect: %s (%s).", socket, reason, code)
            await self.close_socket(socket)
            return

        LOGGER.info("%r was disconnected (%s). Attempting to reconnect...", socket, code)
        await self.reconnect_socket(socket=socket, soft=code in SOFT_FAIL_CODES)

    async def reconnect_socket(self, socket: Websocket, *, soft: bool = False) -> ...: ...

    async def open_socket(self) -> ...:
        # TODO: ...

        ws = Websocket(self)
        await ws.open(keepalive=self._keepalive)

    async def batch_open(self) -> ...: ...

    async def close_socket(self, socket: Websocket) -> ...: ...

    async def batch_close(self) -> ...: ...

    async def shutdown(self) -> ...: ...

    async def _dispatch_notification(self, socket: Websocket, *, data: NotificationMessage) -> ...: ...

    async def _dispatch_session_reconnect(self, socket: Websocket, *, data: ReconnectMessage, received_at: float) -> ...: ...

    async def _dispatch_session_welcome(self, socket: Websocket, *, data: WelcomeMessage, received_at: float) -> ...:
        LOGGER.debug("Received 'session_welcome' on %r: %s", socket, data)

        socket._session_id = data["payload"]["session"]["id"]
        socket.set_ready()

    async def _dispatch_revocation(self, socket: Websocket, *, data: RevocationMessage, received_at: float) -> ...: ...

    def _wrap_notification(self, socket: Websocket, *, message: NotificationMessage) -> None:
        task = asyncio.create_task(self._dispatch_notification(socket, data=message))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _process_message(self, socket: Websocket, *, data: tuple[float, Any]) -> None:
        try:
            received, message = data
            metadata: MetaData = message["metadata"]
            message_type: MessageTypes = metadata["message_type"]
        except Exception as e:
            LOGGER.error("Unknown exception processing message in %r: %s. Data: %s", socket, e, data, exc_info=e)
            return

        if message_type == "session_keepalive":
            LOGGER.debug("Received 'session_keepalive' on %r: %s", socket, data)
            return

        elif message_type == "notification":
            self._wrap_notification(socket, message=message)
            return

        coro = getattr(self, f"_dispatch_{message_type}", None)
        if not coro:
            LOGGER.warning("Unknown message type received for %r: %s", socket, data)
            return

        await coro(socket, data=message, received_at=received)

    async def _socket_channel(self, socket: Websocket, listener: WebsocketFrame) -> None:
        messages = listener._messages

        while not listener._stop_reading:
            try:
                data: tuple[float, Any] = await messages.get()
            except asyncio.QueueShutDown:
                break

            try:
                await self._process_message(socket, data=data)
            except asyncio.CancelledError:
                raise
            except Exception:
                # TODO: Handling/Logging...
                ...
            finally:
                messages.task_done()

        LOGGER.debug("%r message consumer has gracefully terminated.", socket)


class WebsocketFrame(WSListener):
    def __init__(self, socket: Websocket) -> None:
        super().__init__()

        self._socket = socket
        self._close_code: WSCloseCode | None = None
        self._close_reason: str | None = None
        self._close_expected: bool = False
        self._stop_reading: bool = False
        self._messages: asyncio.Queue[tuple[float, Any]] = asyncio.Queue()

    def on_ws_frame(self, transport: WSTransport, frame: WSFrame) -> None:
        if self._stop_reading:
            return

        if frame.msg_type is WSMsgType.TEXT:
            try:
                data = JSON_LOADS(frame.get_payload_as_bytes())
            except Exception as e:
                LOGGER.error("Unable to process message for %r: %r", self._socket, frame, exc_info=e)
                return

            try:
                self._messages.put_nowait((time.monotonic(), data))
            except asyncio.QueueShutDown:
                return

            self._socket.ack()
            return

        if frame.msg_type is not WSMsgType.CLOSE:
            return

        self._close_code = frame.get_close_code()
        self._close_reason = frame.get_close_reason()

        LOGGER.debug("%r received CLOSE %s: %s", self._socket, self._close_code, self._close_reason)
        self._stop_reading = True
        transport.send_close(WSCloseCode.OK)
        transport.disconnect()


class Websocket:
    __slots__ = (
        "_channel_task",
        "_closing",
        "_last_ack",
        "_opening",
        "_ready_event",
        "_session_id",
        "_watcher_task",
        "container",
    )

    def __init__(self, manager: WebsocketManager) -> None:
        self.container: WSContainer = WSContainer(manager=manager, listener=None, transport=None)

        self._session_id: str | None = None
        self._ready_event = asyncio.Event()
        self._last_ack: float = time.monotonic()
        self._channel_task: asyncio.Task[None] | None = None
        self._watcher_task: asyncio.Task[None] | None = None
        self._opening: bool = False
        self._closing: bool = False

    @property
    def manager(self) -> WebsocketManager:
        return self.container.manager

    @property
    def listener(self) -> WebsocketFrame | None:
        return self.container.listener

    @property
    def transport(self) -> WSTransport | None:
        return self.container.transport

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @property
    def is_ready(self) -> bool:
        return self._ready_event.is_set()

    @property
    def is_open(self) -> bool:
        return bool(self.transport and not self.transport.is_disconnected)

    @property
    def last_ack(self) -> float:
        return self._last_ack

    def listener_factory(self) -> WebsocketFrame:
        return WebsocketFrame(self)

    async def open(self, *, uri: str = MISSING, keepalive: int = MIN_KEEP_ALIVE) -> None:
        if self._closing or self._opening:
            # TODO: Error?
            return

        self._opening = True
        self._ready_event.clear()

        if uri is MISSING:
            uri = f"{WSS_URL}?keepalive_timeout_seconds={keepalive}"

        try:
            transport, listener = await ws_connect(url=uri, ws_listener_factory=self.listener_factory)
            if self._closing:
                transport.send_close(WSCloseCode.OK)
                transport.disconnect()
                return self.cleanup()
        finally:
            self._opening = False

        self.container.transport = transport
        self.container.listener = cast("WebsocketFrame", listener)
        self._start_background_tasks()

    async def close(self, *, code: WSCloseCode = WSCloseCode.OK, force: bool = False) -> None:
        if self._closing:
            return

        self._closing = True
        if self._opening:
            return

        if self.listener:
            self.listener._close_expected = True

        if self.transport and not self.transport.is_disconnected:
            await self._cleanup_transport(code)

        if self.listener:
            try:
                await self.drain(self.listener, immediate=force)
            except TimeoutError:
                LOGGER.debug("%r message consumer could not drain gracefully. Disregarding any remaining messages.", self)
            finally:
                self.listener._stop_reading = True

        self.cleanup()

    async def _cleanup_transport(self, code: WSCloseCode) -> None:
        assert self.transport
        self.transport.send_close(code)
        self.transport.disconnect()

        try:
            async with asyncio.timeout(CLEANUP_TIMEOUT):
                await self.transport.wait_disconnected()
        except TimeoutError:
            pass

    def cleanup(self) -> None:
        current = asyncio.current_task()

        for task in (self._channel_task, self._watcher_task):
            if task is not None and task is not current:
                task.cancel()

        self._ready_event.clear()
        self._session_id = None
        self.container.listener = None
        self.container.transport = None
        self._channel_task = None
        self._watcher_task = None

        self._closing = False

    async def drain(self, listener: WebsocketFrame, *, immediate: bool = False) -> None:
        listener._messages.shutdown(immediate=immediate)

        async with asyncio.timeout(CLEANUP_TIMEOUT):
            await listener._messages.join()

    async def resume(self) -> None: ...

    def _start_background_tasks(self) -> None:
        if self._channel_task or self._watcher_task:
            raise WebsocketException("Cannot duplicate websocket background tasks. A channel is already running.")

        LOGGER.debug("Starting background tasks on websocket %r", self)

        assert self.listener
        self._channel_task = asyncio.create_task(self.manager._socket_channel(self, self.listener))
        self._watcher_task = asyncio.create_task(self._watcher(self.listener))

    async def _watcher(self, listener: WebsocketFrame) -> None:
        assert self.transport and self.listener
        error: Exception | None = None

        try:
            await self.transport.wait_disconnected()
        except Exception as e:
            error = e

        if listener._close_expected:
            LOGGER.debug("Ignoring expected closure in %r.", self)
            return

        if listener is not self.listener:
            LOGGER.debug("Ignoring closure from a superseded listener in %r. Twitch has likely resumed this socket.", self)
            return

        task = asyncio.create_task(self.manager._handle_reconnect(self, listener=listener, error=error))
        self.manager._tasks.add(task)
        task.add_done_callback(self.manager._tasks.discard)

    def ack(self) -> None:
        self._last_ack = time.monotonic()

    def set_ready(self) -> None:
        self._ready_event.set()

    async def wait_for_ready(self) -> None:
        async with asyncio.timeout(MIN_KEEP_ALIVE):
            await self._ready_event.wait()
