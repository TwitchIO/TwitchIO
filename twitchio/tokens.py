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

import asyncio
import copy
import pathlib
from typing import Protocol, TypedDict, NotRequired, Any
from collections.abc import MutableMapping

from .utils import JSON_DUMPS, JSON_LOADS


class TokenDictT(TypedDict):
    user_id: str
    access_token: str
    refresh_token: str
    expires_in: NotRequired[int]


class TokenManagerProtocol(Protocol):
    tokens: MutableMapping[str, TokenDictT]

    async def save(self) -> None: ...

    async def load(self) -> None: ...

    async def add(self, data: Any, *, user_id: str) -> None: ...

    async def remove(self, user: str) -> None: ...

    def get(self, user: ...) -> ...: ...


class BaseTokenManager(TokenManagerProtocol):
    def __init__(self) -> None:
        self._lock: asyncio.Lock = asyncio.Lock()
        self.tokens: MutableMapping[str, TokenDictT] = {}

    async def save(self, *, override: bool = True) -> None:
        tokens = copy.deepcopy(self.tokens)
        cwd = pathlib.Path.cwd()
        fp = cwd / ".__tio__.tokens.json"

        if not override and fp.exists():
            return

        async with self._lock:
            with fp.open("w", encoding="utf-8") as f:
                f.write(JSON_DUMPS(tokens))

            fp.chmod(0o600)

    async def load(self) -> None:
        cwd = pathlib.Path.cwd()

        fp = cwd / ".__tio__.tokens.json"
        if not fp.exists():
            return

        async with self._lock:
            with fp.open("r", encoding="utf-8") as f:
                self.tokens.update(JSON_LOADS(f.read()))

    async def add(self, data: Any, *, user_id: str) -> None:
        new: TokenDictT = {
            "user_id": user_id,
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_in": data.get("expires_in"),
        }
        self.tokens[user_id] = new

    async def remove(self, user: str) -> None:
        self.tokens.pop(user, None)

    def get(self, user: str) -> TokenDictT | None:
        return self.tokens.get(user)
