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

from types import get_original_bases
from typing import (
    Any,
    ClassVar,
    Literal,
    NotRequired,
    Required,
    Unpack,
    get_args,
    get_origin,
    get_type_hints,
    is_typeddict,
)

from ..enums import SubscriptionType
from ..exceptions import MissingConditionError
from ..http import Route
from .conditions import *


__all__ = ("ChatMessageSubscription", "Subscription")

# TODO: Doc generic classes


class _BaseSubscription[T]:
    method: ClassVar[Literal["POST"]] = "POST"
    path: ClassVar[Literal["eventsub/subscriptions"]] = "eventsub/subscriptions"
    type: SubscriptionType
    version: str
    scopes: ClassVar[...]
    __condition_keys__: ClassVar[frozenset[str]] = frozenset()
    __condition_required__: ClassVar[frozenset[str]] = frozenset()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        bases = get_original_bases(cls)

        for base in bases:
            origin = get_origin(base)
            if not isinstance(origin, type) or not issubclass(origin, _BaseSubscription):
                continue

            for arg in get_args(base):
                if not is_typeddict(arg):
                    continue

                hints = get_type_hints(arg, include_extras=True)
                cls.__condition_keys__ = frozenset(hints)
                cls.__condition_required__ = frozenset(
                    key
                    for key, hint in hints.items()
                    if get_origin(hint) is Required or (arg.__total__ and get_origin(hint) is not NotRequired)
                )

        super().__init_subclass__(**kwargs)

    def __init__(self, *, condition: T, type: SubscriptionType, version: str) -> None:
        self._condition: T = condition
        self._check_condition(condition)

        self.type = type
        self.version = version
        self._data = {"type": self.type, "version": self.version, "condition": self._condition}

    def _check_condition(self, condition: Any) -> None:
        provided = set(condition)
        allowed = self.__condition_keys__
        required = self.__condition_required__

        if not provided:
            expected = ", ".join(map(repr, sorted(allowed)))
            raise MissingConditionError(
                f"At least one condition keyword argument is required for {type(self).__name__}: {expected}"
            )

        missing = required - provided
        if missing:
            names = ", ".join(map(repr, sorted(missing)))
            raise MissingConditionError(f"Missing required condition keyword argument(s) for {type(self).__name__}: {names}")

        unexpected = provided - allowed
        if unexpected:
            names = ", ".join(map(repr, sorted(unexpected)))
            raise ValueError(f"Unexpected condition keyword argument(s) for {type(self).__name__}: {names}")

    def route(self) -> Route:
        return Route(self.method, self.path, data=self._data)

    @property
    def condition(self) -> T:
        return self._condition


class Subscription[T](_BaseSubscription[T]):
    """Base subscription class used to make an EventSub subscription to Twitch.

    Parameters
    ----------
    condition: ...
        ...
    type: ...
        ...
    version: ...
        ...

    Attributes
    ----------
    method: ClassVar[Literal["POST"]]
        The HTTP method used to make the subscription request. This will always be ``"POST"``.
    path: ClassVar[Literal["eventsub/subscriptions"]]
        The HTTP path used to make the subscription request. This will aluways be ``"eventsub/subscriptions"``.
    type: str
        The eventsub subscription type passed to Twitch. E.g. ``"channel.chat.message"``.
        See: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/ for more info.
    version: str
        The eventsub subscription version passed to Twitch. E.g. ``"1"``.
        See: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/ for more info.
    scopes: ...
        ...
    """

    def __init__(self, *, condition: T, type: SubscriptionType, version: str) -> None:
        super().__init__(condition=condition, type=type, version=version)


class ChatMessageSubscription(Subscription[ChannelChatMessageCT]):
    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChatMessage
    _version: ClassVar[str] = "1"
    scopes: ClassVar[...]

    def __init__(self, **condition: Unpack[ChannelChatMessageCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)
