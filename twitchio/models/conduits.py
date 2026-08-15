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

from typing import TYPE_CHECKING, Unpack

from .base import BaseModel


if TYPE_CHECKING:
    from ..types_.eventsub import ConduitData


__all__ = ("Conduit", "ConduitShard")


class Conduit(BaseModel):
    __slots__ = ("_id", "_shard_count")

    def __init__(self, **data: Unpack[ConduitData]) -> None:
        self._id = data["id"]
        self._shard_count = data["shard_count"]

    @property
    def id(self) -> str:
        return self._id

    @property
    def shard_count(self) -> int:
        return self._shard_count

    async def fetch_shards(self) -> list[ConduitShard]: ...

    async def delete(self) -> None: ...

    async def update(self, count: int, /) -> None:
        if not 1 <= count <= 20_000:
            raise ValueError("Provided shard count is not within limits. Conduit shard count must be between 1 and 20_000.")

        await self._http.update_conduits(id=self._id, shard_count=count)

    async def update_shards(self) -> ...: ...


class ConduitShard:
    __slots__ = ()
