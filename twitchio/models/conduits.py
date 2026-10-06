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

from typing import TYPE_CHECKING, Any, NamedTuple, Self, Unpack

from ..exceptions import HTTPException
from .base import BaseModel, IdentifiableBaseModel, model_transform


if TYPE_CHECKING:
    from collections.abc import Collection

    from twitchio.types_.eventsub import SubscriptionCreateRequest, SubscriptionCreateTransport

    from ..eventsub.subscriptions import Subscription
    from ..types_.eventsub import AnyCondition, ConduitData, ShardData
    from ..types_.responses import UpdateConduitsShardsError, UpdateConduitsShardsResponseT


__all__ = ("Conduit", "ConduitShard", "UpdatedShardPayload")


class SubscriptionError(NamedTuple):
    subscription: Subscription[AnyCondition]
    error: HTTPException


@model_transform()
class SubscriptionResults(BaseModel):
    __slots__ = ("errors", "successful")

    def __init__(self, *, success: list[Subscription[AnyCondition]], errors: list[SubscriptionError]) -> None:
        self.successful: list[Subscription[AnyCondition]] = success
        self.errors: list[SubscriptionError] = errors


@model_transform(frozen=False)
class Conduit(IdentifiableBaseModel):
    __slots__ = ("_shard_count", "id")

    def __init__(self, **data: Unpack[ConduitData]) -> None:
        self.id: str = data["id"]
        self._shard_count: int = data["shard_count"]

    def __repr__(self) -> str:
        return f"Conduit(id={self.id}, shard_count={self._shard_count})"

    def __int__(self) -> int:
        return self._shard_count

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Conduit):
            return NotImplemented

        return self._shard_count > other._shard_count

    @property
    def shard_count(self) -> int:
        return self._shard_count

    async def update(self) -> Self:
        resp = await self._http._get_conduits()

        for conduit in resp["data"]:
            if conduit["id"] == self.id:
                self._shard_count = conduit["shard_count"]

        return self

    # TODO: Limit / status
    async def fetch_shards(self) -> list[ConduitShard]:
        shards = [ConduitShard(**resp) async for resp in self._http.get_conduit_shards(conduit_id=self.id)]
        return shards

    async def delete(self) -> None:
        await self._http.delete_conduit(id=self.id)

    async def scale(self, count: int, /) -> None:
        if not 1 <= count <= 20_000:
            raise ValueError("Provided shard count is not within limits. Conduit shard count must be between 1 and 20_000.")

        await self._http.update_conduits(id=self.id, shard_count=count)
        self._shard_count = count

    async def update_shards(self) -> ...: ...

    async def subscribe(self, subscriptions: Collection[Subscription[Any]]) -> SubscriptionResults:
        transport: SubscriptionCreateTransport = {"method": "conduit", "conduit_id": self.id}

        success: list[Subscription[Any]] = []
        errors: list[SubscriptionError] = []

        for sub in subscriptions:
            data: SubscriptionCreateRequest = {
                "type": sub.type,
                "version": sub.version,
                "condition": sub.condition,
                "transport": transport,
            }

            try:
                await self._http.create_eventsub_subscription(**data)
            except HTTPException as e:
                errors.append(SubscriptionError(subscription=sub, error=e))
            else:
                success.append(sub)

        return SubscriptionResults(success=success, errors=errors)

    async def unsubscribe(self, subscriptions: Collection[Subscription[Any]]) -> ...: ...


@model_transform()
class ConduitShard(IdentifiableBaseModel):
    __slots__ = ("id", "status", "transport")

    def __init__(self, **data: Unpack[ShardData]) -> None:
        self.id = data["id"]
        self.status = data["status"]
        self.transport = data["transport"]  # TODO: ...


@model_transform()
class UpdatedShardPayload(BaseModel):
    __slots__ = ("errors", "shards")

    def __init__(self, **data: Unpack[UpdateConduitsShardsResponseT]) -> None:
        self.shards: list[ConduitShard] = [ConduitShard(**i) for i in data["data"]]  # type: ignore[arg-type]
        self.errors: list[UpdateConduitsShardsError] = data["errors"]
