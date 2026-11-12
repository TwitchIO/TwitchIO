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

from typing import Any, overload


class LookupStack[T]:
    def __init__(self, maxlen: int = 500) -> None:
        if maxlen <= 0:
            raise ValueError("maxlen must be greater than 0.")

        self._stack: dict[Any, T] = {}
        self._maxlen = maxlen

    def __getitem__(self, key: Any) -> T:
        return self._stack[key]

    def __contains__(self, key: Any) -> bool:
        return key in self._stack

    def __len__(self) -> int:
        return len(self._stack)

    def __repr__(self) -> str:
        return f"LookupStack({self._stack})"

    @overload
    def get(self, key: Any) -> T | None: ...

    @overload
    def get[DT](self, key: Any, default: DT) -> T | DT: ...

    def get[DT](self, key: Any, default: DT = None) -> T | DT | None:
        return self._stack.get(key, default)

    def push(self, key: Any, item: T) -> None:
        if key in self._stack:
            del self._stack[key]

        if len(self._stack) >= self._maxlen:
            self._stack.pop(next(iter(self._stack)), None)

        self._stack[key] = item
