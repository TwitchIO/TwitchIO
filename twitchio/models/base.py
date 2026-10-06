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

import types
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Self, TypeVar

from ..utils import MISSING


if TYPE_CHECKING:
    from collections.abc import Callable

    from ..http import HTTPClient


T = TypeVar("T", bound="BaseModel")


def _eq_id(self: Any, other: Any) -> bool:
    kind = getattr(other, "__id_kind__", MISSING)
    if kind is MISSING or kind != self.__id_kind__:
        return NotImplemented

    return self.id == other.id


def _hash_id(self: IdentifiableBaseModel) -> int:
    return hash(self.id)


class Identifiable(Protocol):
    __id_kind__: ClassVar[str]
    id: str
    __hash__: Callable[[Self], int]
    __eq__: Callable[[Self, Any], bool]


class BaseModel:
    __slots__ = ()
    __http: ClassVar[HTTPClient]

    @property
    def _http(self) -> HTTPClient:
        return self.__http


class IdentifiableBaseModel(BaseModel):
    __slots__ = ()
    __id_kind__: ClassVar[str]
    id: str
    __hash__ = _hash_id
    __eq__ = _eq_id


class FrozenBaseModel(BaseModel):
    __slots__ = ()

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, name):
            raise TypeError(f"Cannot mutate attribute '{name}' of frozen {type(self).__name__}.")

        object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        raise TypeError(f"Cannot mutate attribute '{name}' of frozen {type(self).__name__}")


def model_transform(*, frozen: bool = True) -> Callable[[type[T]], type[T]]:
    def wrapper(cls: type[T]) -> type[T]:
        if frozen and not cls.__dict__.get("__slots__"):
            raise TypeError("Cannot create a frozen model without '__slots__'.")

        ns: dict[str, Any] = {
            "__slots__": (),
            "__module__": cls.__module__,
            "__qualname__": cls.__qualname__,
            "__doc__": cls.__doc__,
        }

        if cls is IdentifiableBaseModel or issubclass(cls, IdentifiableBaseModel):
            ns["__eq__"] = _eq_id
            ns["__hash__"] = _hash_id
            
            if not ns.get("__id_kind__"):
                ns["__id_kind__"] = cls.__name__

        bases = (cls, FrozenBaseModel) if frozen else (cls,)
        return types.new_class(cls.__name__, bases, exec_body=lambda body: body.update(ns))

    return wrapper
