"""
The MIT License (MIT)

Copyright (c) 2021-Present TwitchIO, PythonistaGuild, EvieePy, Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from collections import OrderedDict
from collections.abc import Hashable, Iterator
from typing import overload


class BoundedCache[K: Hashable, V]:
    __slots__ = ("_data", "_lru", "_maxlen")

    def __init__(self, maxlen: int = 500, *, lru: bool = False) -> None:
        if maxlen < 1:
            raise ValueError("maxlen must be >= 1.")

        self._data: OrderedDict[K, V] = OrderedDict()
        self._maxlen = maxlen
        self._lru = lru

    def __getitem__(self, key: K) -> V:
        value = self._data[key]

        if self._lru:
            self._data.move_to_end(key)

        return value

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(len={len(self)}, maxlen={self._maxlen})"

    @overload
    def get(self, key: K) -> V | None: ...

    @overload
    def get[D](self, key: K, default: D) -> V | D: ...

    def get[D](self, key: K, default: D | None = None) -> V | D | None:
        try:
            return self[key]
        except KeyError:
            return default

    def push(self, key: K, item: V) -> None:
        self._data[key] = item
        self._data.move_to_end(key)

        if len(self._data) > self._maxlen:
            self._data.popitem(last=False)

    def pop(self, key: K) -> V:
        return self._data.pop(key)

    def clear(self) -> None:
        self._data.clear()
