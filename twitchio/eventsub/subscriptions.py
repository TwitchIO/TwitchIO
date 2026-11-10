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


__all__ = (
    "AdBreakBeginSubscription",
    "AutomodMessageHoldSubscription",
    "AutomodMessageHoldV2Subscription",
    "AutomodMessageUpdateSubscription",
    "AutomodMessageUpdateV2Subscription",
    "AutomodSettingsUpdateSubscription",
    "AutomodTermsUpdateSubscription",
    "ChannelBanSubscription",
    "ChannelBitsUseSubscription",
    "ChannelCheerSubscription",
    "ChannelFollowSubscription",
    "ChannelModerateSubscription",
    "ChannelModerateV2Subscription",
    "ChannelModeratorAddSubscription",
    "ChannelModeratorRemoveSubscription",
    "ChannelPointsAutoRedeemSubscription",
    "ChannelPointsAutoRedeemV2Subscription",
    "ChannelPointsRedeemAddSubscription",
    "ChannelPointsRedeemUpdateSubscription",
    "ChannelPointsRewardAddSubscription",
    "ChannelPointsRewardRemoveSubscription",
    "ChannelPointsRewardUpdateSubscription",
    "ChannelPollBeginSubscription",
    "ChannelPollEndSubscription",
    "ChannelPollProgressSubscription",
    "ChannelPredictionBeginSubscription",
    "ChannelPredictionEndSubscription",
    "ChannelPredictionLockSubscription",
    "ChannelPredictionProgressSubscription",
    "ChannelRaidSubscription",
    "ChannelSubscribeMessageSubscription",
    "ChannelSubscribeSubscription",
    "ChannelSubscriptionEndSubscription",
    "ChannelSubscriptionGiftSubscription",
    "ChannelUnbanRequestResolveSubscription",
    "ChannelUnbanRequestSubscription",
    "ChannelUnbanSubscription",
    "ChannelUpdateSubscription",
    "ChannelVIPAddSubscription",
    "ChannelVIPRemoveSubscription",
    "ChannelWarningAcknowledgementSubscription",
    "ChannelWarningSendSubscription",
    "CharityCampaignProgressSubscription",
    "CharityCampaignStartSubscription",
    "CharityCampaignStopSubscription",
    "CharityDonationSubscription",
    "ChatClearSubscription",
    "ChatClearUserMessagesSubscription",
    "ChatMessageDeleteSubscription",
    "ChatMessageSubscription",
    "ChatNotificationSubscription",
    "ChatSettingsUpdateSubscription",
    "ChatUserMessageHoldSubscription",
    "ChatUserMessageUpdateSubscription",
    "ConduitShardDisabledSubscription",
    "CustomPowerupRedeemAddSubscription",
    "DropEntitlementGrantSubscription",
    "ExtensionBitsTransactionCreateSubscription",
    "GoalBeginSubscription",
    "GoalEndSubscription",
    "GoalProgressSubscription",
    "GuestStarGuestUpdateSubscription",
    "GuestStarSessionBeginSubscription",
    "GuestStarSessionEndSubscription",
    "GuestStarSettingsUpdateSubscription",
    "HypeTrainBeginSubscription",
    "HypeTrainEndSubscription",
    "HypeTrainProgressSubscription",
    "SharedChatSessionBeginSubscription",
    "SharedChatSessionEndSubscription",
    "SharedChatSessionUpdateSubscription",
    "ShieldModeBeginSubscription",
    "ShieldModeEndSubscription",
    "ShoutoutCreateSubscription",
    "ShoutoutReceiveSubscription",
    "StreamOfflineSubscription",
    "StreamOnlineSubscription",
    "Subscription",
    "SuspiciousUserMessageSubscription",
    "SuspiciousUserUpdateSubscription",
    "UserAuthorizationGrantSubscription",
    "UserAuthorizationRevokeSubscription",
    "UserUpdateSubscription",
    "WhisperReceivedSubscription",
)

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

        if not cls.__condition_keys__:
            cls.__condition_keys__ = frozenset(get_type_hints(_ConditionCT, include_extras=True))

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

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Subscription):
            return NotImplemented

        return self.type == other.type and self.version == other.version and self.condition == other.condition  # type: ignore[Reason: Subscription Generic is always AnyCondition]

    def __hash__(self) -> int:
        return hash((self.type, self.version, frozenset(self.condition.items())))  # type: ignore[Reason: Subscription Generic is always AnyCondition]


class AutomodMessageHoldSubscription(Subscription[AutomodMessageHoldCT]):
    """Subscription for ``automod.message.hold`` (version ``1``).

    Sends a notification when a message is held by AutoMod for review.

    .. important::
        Requires the ``moderator:manage:automod`` scope from the user in ``moderator_user_id``, who must be a moderator of
        the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.AutomodMessageHold
    _version: ClassVar[str] = "1"
    scopes = ...  # moderator:manage:automod

    def __init__(self, **condition: Unpack[AutomodMessageHoldCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class AutomodMessageHoldV2Subscription(Subscription[AutomodMessageHoldCT]):
    """Subscription for ``automod.message.hold`` (version ``2``).

    Sends a notification when a message is held by AutoMod for review. Only public blocked terms trigger notifications, not
    private ones.

    .. important::
        Requires the ``moderator:manage:automod`` scope from the user in ``moderator_user_id``, who must be a moderator of
        the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.AutomodMessageHold
    _version: ClassVar[str] = "2"
    scopes = ...  # moderator:manage:automod

    def __init__(self, **condition: Unpack[AutomodMessageHoldCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class AutomodMessageUpdateSubscription(Subscription[AutomodMessageUpdateCT]):
    """Subscription for ``automod.message.update`` (version ``1``).

    Sends a notification when a message in the AutoMod queue has its status changed.

    .. important::
        Requires the ``moderator:manage:automod`` scope from the user in ``moderator_user_id``, who must be a moderator of
        the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.AutomodMessageUpdate
    _version: ClassVar[str] = "1"
    scopes = ...  # moderator:manage:automod

    def __init__(self, **condition: Unpack[AutomodMessageUpdateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class AutomodMessageUpdateV2Subscription(Subscription[AutomodMessageUpdateCT]):
    """Subscription for ``automod.message.update`` (version ``2``).

    Sends a notification when a message in the AutoMod queue has its status changed. Only public blocked terms trigger
    notifications, not private ones.

    .. important::
        Requires the ``moderator:manage:automod`` scope from the user in ``moderator_user_id``, who must be a moderator of
        the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.AutomodMessageUpdate
    _version: ClassVar[str] = "2"
    scopes = ...  # moderator:manage:automod

    def __init__(self, **condition: Unpack[AutomodMessageUpdateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class AutomodSettingsUpdateSubscription(Subscription[AutomodSettingsUpdateCT]):
    """Subscription for ``automod.settings.update`` (version ``1``).

    Sends a notification when the broadcaster's AutoMod settings are updated.

    .. important::
        Requires the ``moderator:read:automod_settings`` scope from the user in ``moderator_user_id``, who must be a
        moderator of the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.AutomodSettingsUpdate
    _version: ClassVar[str] = "1"
    scopes = ...  # moderator:read:automod_settings

    def __init__(self, **condition: Unpack[AutomodSettingsUpdateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class AutomodTermsUpdateSubscription(Subscription[AutomodTermsUpdateCT]):
    """Subscription for ``automod.terms.update`` (version ``1``).

    Sends a notification when the broadcaster's AutoMod terms are updated. Changes to private terms are not sent.

    .. important::
        Requires the ``moderator:manage:automod`` scope from the user in ``moderator_user_id``, who must be a moderator of
        the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.AutomodTermsUpdate
    _version: ClassVar[str] = "1"
    scopes = ...  # moderator:manage:automod

    def __init__(self, **condition: Unpack[AutomodTermsUpdateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelBitsUseSubscription(Subscription[ChannelBitUseCT]):
    """Subscription for ``channel.bits.use`` (version ``1``).

    Sends a notification whenever Bits are used on the channel: cheers, Power-ups and custom Power-ups. Bits spent through
    Extensions are not included.

    .. important::
        Requires a user access token with the ``bits:read`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelBitsUse
    _version: ClassVar[str] = "1"
    scopes = ...  # bits:read

    def __init__(self, **condition: Unpack[ChannelBitUseCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelUpdateSubscription(Subscription[ChannelUpdateCT]):
    """Subscription for ``channel.update`` (version ``2``).

    Sends a notification when the broadcaster updates their channel's title, category, broadcast language or content
    classification labels.

    .. important::
        No authorization required.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelUpdate
    _version: ClassVar[str] = "2"
    scopes = ...  # No scopes required

    def __init__(self, **condition: Unpack[ChannelUpdateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelFollowSubscription(Subscription[ChannelFollowCT]):
    """Subscription for ``channel.follow`` (version ``2``).

    Sends a notification when the channel receives a follow.

    .. important::
        Requires the ``moderator:read:followers`` scope from the user in ``moderator_user_id``, who must be a moderator of
        the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelFollow
    _version: ClassVar[str] = "2"
    scopes = ...  # moderator:read:followers

    def __init__(self, **condition: Unpack[ChannelFollowCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class AdBreakBeginSubscription(Subscription[ChannelAdBreakBeginCT]):
    """Subscription for ``channel.ad_break.begin`` (version ``1``).

    Sends a notification when a midroll commercial break starts, whether run manually or automatically by the Ads Manager.

    .. important::
        Requires the ``channel:read:ads`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelAdBreakBegin
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:ads

    def __init__(self, **condition: Unpack[ChannelAdBreakBeginCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChatClearSubscription(Subscription[ChannelChatClearCT]):
    """Subscription for ``channel.chat.clear`` (version ``1``).

    Sends a notification when a moderator or bot clears all messages from the chat room.

    .. important::
        Requires the ``user:read:chat`` scope from the chatting user in ``user_id``. When using an app access token, the
        chatting user must also have granted ``user:bot``, and the broadcaster must have granted ``channel:bot`` (or the
        chatting user must be a moderator of the channel).

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    user_id: str
        The ID of the user to read chat as. With a user access token this must match the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChatClear
    _version: ClassVar[str] = "1"
    scopes = ...  # user:read:chat (app token: also user:bot, and channel:bot or moderator status)

    def __init__(self, **condition: Unpack[ChannelChatClearCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChatClearUserMessagesSubscription(Subscription[ChannelChatClearUserMessagesCT]):
    """Subscription for ``channel.chat.clear_user_messages`` (version ``1``).

    Sends a notification when a moderator or bot clears all messages from a specific user.

    .. important::
        Requires the ``user:read:chat`` scope from the chatting user in ``user_id``. When using an app access token, the
        chatting user must also have granted ``user:bot``, and the broadcaster must have granted ``channel:bot`` (or the
        chatting user must be a moderator of the channel).

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    user_id: str
        The ID of the user to read chat as. With a user access token this must match the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChatClearUserMessages
    _version: ClassVar[str] = "1"
    scopes = ...  # user:read:chat (app token: also user:bot, and channel:bot or moderator status)

    def __init__(self, **condition: Unpack[ChannelChatClearUserMessagesCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChatMessageSubscription(Subscription[ChannelChatMessageCT]):
    """Subscription for ``channel.chat.message`` (version ``1``).

    Sends a notification when any user sends a message to the chat room.

    .. important::
        Requires the ``user:read:chat`` scope from the chatting user in ``user_id``. When using an app access token, the
        chatting user must also have granted ``user:bot``, and the broadcaster must have granted ``channel:bot`` (or the
        chatting user must be a moderator of the channel).

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    user_id: str
        The ID of the user to read chat as. With a user access token this must match the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChatMessage
    _version: ClassVar[str] = "1"
    scopes = ...  # user:read:chat (app token: also user:bot, and channel:bot or moderator status)

    def __init__(self, **condition: Unpack[ChannelChatMessageCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChatMessageDeleteSubscription(Subscription[ChannelChatMessageDeleteCT]):
    """Subscription for ``channel.chat.message_delete`` (version ``1``).

    Sends a notification when a moderator removes a specific message.

    .. important::
        Requires the ``user:read:chat`` scope from the chatting user in ``user_id``. When using an app access token, the
        chatting user must also have granted ``user:bot``, and the broadcaster must have granted ``channel:bot`` (or the
        chatting user must be a moderator of the channel).

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    user_id: str
        The ID of the user to read chat as. With a user access token this must match the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChatMessageDelete
    _version: ClassVar[str] = "1"
    scopes = ...  # user:read:chat (app token: also user:bot, and channel:bot or moderator status)

    def __init__(self, **condition: Unpack[ChannelChatMessageDeleteCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChatNotificationSubscription(Subscription[ChannelChatNotificationCT]):
    """Subscription for ``channel.chat.notification`` (version ``1``).

    Sends a notification when an event that appears in chat occurs, such as a subscription, gifted subscription, raid or
    announcement.

    .. important::
        Requires the ``user:read:chat`` scope from the chatting user in ``user_id``. When using an app access token, the
        chatting user must also have granted ``user:bot``, and the broadcaster must have granted ``channel:bot`` (or the
        chatting user must be a moderator of the channel).

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    user_id: str
        The ID of the user to read chat as. With a user access token this must match the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChatNotification
    _version: ClassVar[str] = "1"
    scopes = ...  # user:read:chat (app token: also user:bot, and channel:bot or moderator status)

    def __init__(self, **condition: Unpack[ChannelChatNotificationCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChatSettingsUpdateSubscription(Subscription[ChannelChatSettingsUpdateCT]):
    """Subscription for ``channel.chat_settings.update`` (version ``1``).

    Sends a notification when the broadcaster's chat settings are updated.

    .. important::
        Requires the ``user:read:chat`` scope from the chatting user in ``user_id``. When using an app access token, the
        chatting user must also have granted ``user:bot``, and the broadcaster must have granted ``channel:bot`` (or the
        chatting user must be a moderator of the channel).

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    user_id: str
        The ID of the user to read chat as. With a user access token this must match the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChatSettingsUpdate
    _version: ClassVar[str] = "1"
    scopes = ...  # user:read:chat (app token: also user:bot, and channel:bot or moderator status)

    def __init__(self, **condition: Unpack[ChannelChatSettingsUpdateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChatUserMessageHoldSubscription(Subscription[ChannelChatUserMessageHoldCT]):
    """Subscription for ``channel.chat.user_message_hold`` (version ``1``).

    Notifies the user in ``user_id`` when one of their messages is held by AutoMod.

    .. important::
        Requires the ``user:read:chat`` scope from the user in ``user_id``. When using an app access token, that user must
        also have granted ``user:bot``.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    user_id: str
        The ID of the user to read chat as. With a user access token this must match the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChatUserMessageHold
    _version: ClassVar[str] = "1"
    scopes = ...  # user:read:chat (app token: also user:bot)

    def __init__(self, **condition: Unpack[ChannelChatUserMessageHoldCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChatUserMessageUpdateSubscription(Subscription[ChannelChatUserMessageUpdate]):
    """Subscription for ``channel.chat.user_message_update`` (version ``1``).

    Notifies the user in ``user_id`` when the AutoMod status of one of their held messages is updated.

    .. important::
        Requires the ``user:read:chat`` scope from the user in ``user_id``. When using an app access token, that user must
        also have granted ``user:bot``.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    user_id: str
        The ID of the user to read chat as. With a user access token this must match the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChatUserMessageUpdate
    _version: ClassVar[str] = "1"
    scopes = ...  # user:read:chat (app token: also user:bot)

    def __init__(self, **condition: Unpack[ChannelChatUserMessageUpdate]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class SharedChatSessionBeginSubscription(Subscription[ChannelSharedChatSessionBeginCT]):
    """Subscription for ``channel.shared_chat.begin`` (version ``1``).

    Sends a notification when the channel becomes active in a shared chat session.

    .. important::
        No authorization required.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelSharedChatBegin
    _version: ClassVar[str] = "1"
    scopes = ...  # No scopes required

    def __init__(self, **condition: Unpack[ChannelSharedChatSessionBeginCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class SharedChatSessionUpdateSubscription(Subscription[ChannelSharedChatSessionUpdateCT]):
    """Subscription for ``channel.shared_chat.update`` (version ``1``).

    Sends a notification when the shared chat session the channel is in changes.

    .. important::
        No authorization required.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelSharedChatUpdate
    _version: ClassVar[str] = "1"
    scopes = ...  # No scopes required

    def __init__(self, **condition: Unpack[ChannelSharedChatSessionUpdateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class SharedChatSessionEndSubscription(Subscription[ChannelSharedChatSessionEndCT]):
    """Subscription for ``channel.shared_chat.end`` (version ``1``).

    Sends a notification when the channel leaves a shared chat session, or the session ends.

    .. important::
        No authorization required.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelSharedChatEnd
    _version: ClassVar[str] = "1"
    scopes = ...  # No scopes required

    def __init__(self, **condition: Unpack[ChannelSharedChatSessionEndCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelSubscribeSubscription(Subscription[ChannelSubscribeCT]):
    """Subscription for ``channel.subscribe`` (version ``1``).

    Sends a notification when the channel receives a new subscriber. Resubscriptions are not included.

    .. important::
        Requires the ``channel:read:subscriptions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelSubscribe
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:subscriptions

    def __init__(self, **condition: Unpack[ChannelSubscribeCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelSubscriptionEndSubscription(Subscription[ChannelSubscriptionEndCT]):
    """Subscription for ``channel.subscription.end`` (version ``1``).

    Sends a notification when a subscription to the channel ends.

    .. important::
        Requires the ``channel:read:subscriptions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelSubscriptionEnd
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:subscriptions

    def __init__(self, **condition: Unpack[ChannelSubscriptionEndCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelSubscriptionGiftSubscription(Subscription[ChannelSubscriptionGiftCT]):
    """Subscription for ``channel.subscription.gift`` (version ``1``).

    Sends a notification when a viewer gifts one or more subscriptions in the channel.

    .. important::
        Requires the ``channel:read:subscriptions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelSubscriptionGift
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:subscriptions

    def __init__(self, **condition: Unpack[ChannelSubscriptionGiftCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelSubscribeMessageSubscription(Subscription[ChannelSubscriptionMessageCT]):
    """Subscription for ``channel.subscription.message`` (version ``1``).

    Sends a notification when a user sends a resubscription chat message in the channel.

    .. important::
        Requires the ``channel:read:subscriptions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelSubscriptionMessage
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:subscriptions

    def __init__(self, **condition: Unpack[ChannelSubscriptionMessageCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelCheerSubscription(Subscription[ChannelCheerCT]):
    """Subscription for ``channel.cheer`` (version ``1``).

    Sends a notification when a user cheers in the channel.

    .. important::
        Requires the ``bits:read`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelCheer
    _version: ClassVar[str] = "1"
    scopes = ...  # bits:read

    def __init__(self, **condition: Unpack[ChannelCheerCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelRaidSubscription(Subscription[ChannelRaidCT]):
    """Subscription for ``channel.raid`` (version ``1``).

    Sends a notification when a broadcaster raids another broadcaster's channel.

    .. important::
        No authorization required.

    Parameters
    ----------
    from_broadcaster_user_id: str
        Optional. The ID of the broadcaster sending raids. At least one of ``from_broadcaster_user_id`` or
        ``to_broadcaster_user_id`` must be provided.
    to_broadcaster_user_id: str
        Optional. The ID of the broadcaster receiving raids. At least one of ``from_broadcaster_user_id`` or
        ``to_broadcaster_user_id`` must be provided.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelRaid
    _version: ClassVar[str] = "1"
    scopes = ...  # No scopes required

    def __init__(self, **condition: Unpack[ChannelRaidCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelBanSubscription(Subscription[ChannelBanCT]):
    """Subscription for ``channel.ban`` (version ``1``).

    Sends a notification when a viewer is banned or timed out in the channel.

    .. important::
        Requires the ``channel:moderate`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelBan
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:moderate

    def __init__(self, **condition: Unpack[ChannelBanCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelUnbanSubscription(Subscription[ChannelUnbanCT]):
    """Subscription for ``channel.unban`` (version ``1``).

    Sends a notification when a viewer is unbanned from the channel.

    .. important::
        Requires the ``channel:moderate`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelUnban
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:moderate

    def __init__(self, **condition: Unpack[ChannelUnbanCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelUnbanRequestSubscription(Subscription[ChannelUnbanRequestCreateCT]):
    """Subscription for ``channel.unban_request.create`` (version ``1``).

    Sends a notification when a user creates an unban request.

    .. important::
        Requires the ``moderator:read:unban_requests`` or ``moderator:manage:unban_requests`` scope from the user in
        ``moderator_user_id``, who must be a moderator of the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelUnbanRequestCreate
    _version: ClassVar[str] = "1"
    scopes = ...  # moderator:read:unban_requests or moderator:manage:unban_requests

    def __init__(self, **condition: Unpack[ChannelUnbanRequestCreateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelUnbanRequestResolveSubscription(Subscription[ChannelUnbanRequestResolveCT]):
    """Subscription for ``channel.unban_request.resolve`` (version ``1``).

    Sends a notification when an unban request is resolved.

    .. important::
        Requires the ``moderator:read:unban_requests`` or ``moderator:manage:unban_requests`` scope from the user in
        ``moderator_user_id``, who must be a moderator of the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelUnbanRequestResolve
    _version: ClassVar[str] = "1"
    scopes = ...  # moderator:read:unban_requests or moderator:manage:unban_requests

    def __init__(self, **condition: Unpack[ChannelUnbanRequestResolveCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelModerateSubscription(Subscription[ChannelModerateCT]):
    """Subscription for ``channel.moderate`` (version ``1``).

    Sends a notification when a moderator performs a moderation action in the channel. Some actions affect chatters in other
    channels during shared chat.

    .. important::
        Requires a scope from **each** group below, granted by the user in ``moderator_user_id`` (a moderator of the channel,
        or the broadcaster):

        - ``moderator:read:blocked_terms`` OR ``moderator:manage:blocked_terms``
        - ``moderator:read:chat_settings`` OR ``moderator:manage:chat_settings``
        - ``moderator:read:unban_requests`` OR ``moderator:manage:unban_requests``
        - ``moderator:read:banned_users`` OR ``moderator:manage:banned_users``
        - ``moderator:read:chat_messages`` OR ``moderator:manage:chat_messages``
        - ``moderator:read:moderators``
        - ``moderator:read:vips``

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelModerate
    _version: ClassVar[str] = "1"
    scopes = ...  # (moderator:read:blocked_terms or moderator:manage:blocked_terms), (moderator:read:chat_settings or moderator:manage:chat_settings), (moderator:read:unban_requests or moderator:manage:unban_requests), (moderator:read:banned_users or moderator:manage:banned_users), (moderator:read:chat_messages or moderator:manage:chat_messages), moderator:read:moderators, moderator:read:vips  # fmt: skip

    def __init__(self, **condition: Unpack[ChannelModerateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelModerateV2Subscription(Subscription[ChannelModerateCT]):
    """Subscription for ``channel.moderate`` (version ``2``).

    Sends a notification when a moderator performs a moderation action in the channel, including warnings. Some actions
    affect chatters in other channels during shared chat.

    .. important::
        Requires a scope from **each** group below, granted by the user in ``moderator_user_id`` (a moderator of the channel,
        or the broadcaster):

        - ``moderator:read:blocked_terms`` OR ``moderator:manage:blocked_terms``
        - ``moderator:read:chat_settings`` OR ``moderator:manage:chat_settings``
        - ``moderator:read:unban_requests`` OR ``moderator:manage:unban_requests``
        - ``moderator:read:banned_users`` OR ``moderator:manage:banned_users``
        - ``moderator:read:chat_messages`` OR ``moderator:manage:chat_messages``
        - ``moderator:read:warnings`` OR ``moderator:manage:warnings``
        - ``moderator:read:moderators``
        - ``moderator:read:vips``

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelModerate
    _version: ClassVar[str] = "2"
    scopes = ...  # (moderator:read:blocked_terms or moderator:manage:blocked_terms), (moderator:read:chat_settings or moderator:manage:chat_settings), (moderator:read:unban_requests or moderator:manage:unban_requests), (moderator:read:banned_users or moderator:manage:banned_users), (moderator:read:chat_messages or moderator:manage:chat_messages), (moderator:read:warnings or moderator:manage:warnings), moderator:read:moderators, moderator:read:vips  # fmt: skip

    def __init__(self, **condition: Unpack[ChannelModerateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelModeratorAddSubscription(Subscription[ChannelModeratorAddCT]):
    """Subscription for ``channel.moderator.add`` (version ``1``).

    Sends a notification when moderator privileges are added to a user in the channel.

    .. important::
        Requires the ``moderation:read`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelModeratorAdd
    _version: ClassVar[str] = "1"
    scopes = ...  # moderation:read

    def __init__(self, **condition: Unpack[ChannelModeratorAddCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelModeratorRemoveSubscription(Subscription[ChannelModeratorRemoveCT]):
    """Subscription for ``channel.moderator.remove`` (version ``1``).

    Sends a notification when moderator privileges are removed from a user in the channel.

    .. important::
        Requires the ``moderation:read`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelModeratorRemove
    _version: ClassVar[str] = "1"
    scopes = ...  # moderation:read

    def __init__(self, **condition: Unpack[ChannelModeratorRemoveCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class GuestStarSessionBeginSubscription(Subscription[ChannelGuestStarSessionBeginCT]):
    """Subscription for ``channel.guest_star_session.begin`` (version ``beta``).

    Sends a notification when the host begins a new Guest Star session.

    .. warning::
        This subscription type is in public beta on Twitch, may change at any time, and should not be used in production.

    .. important::
        Requires the ``channel:read:guest_star``, ``channel:manage:guest_star``, ``moderator:read:guest_star`` or
        ``moderator:manage:guest_star`` scope from the user in ``moderator_user_id``, who must be a moderator of the channel
        or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelGuestStarSessionBegin
    _version: ClassVar[str] = "beta"
    scopes = ...  # channel:read:guest_star or channel:manage:guest_star or moderator:read:guest_star or moderator:manage:guest_star  # fmt: skip

    def __init__(self, **condition: Unpack[ChannelGuestStarSessionBeginCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class GuestStarSessionEndSubscription(Subscription[ChannelGuestStarSessionEndCT]):
    """Subscription for ``channel.guest_star_session.end`` (version ``beta``).

    Sends a notification when a running Guest Star session ends.

    .. warning::
        This subscription type is in public beta on Twitch, may change at any time, and should not be used in production.

    .. important::
        Requires the ``channel:read:guest_star``, ``channel:manage:guest_star``, ``moderator:read:guest_star`` or
        ``moderator:manage:guest_star`` scope from the user in ``moderator_user_id``, who must be a moderator of the channel
        or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelGuestStarSessionEnd
    _version: ClassVar[str] = "beta"
    scopes = ...  # channel:read:guest_star or channel:manage:guest_star or moderator:read:guest_star or moderator:manage:guest_star  # fmt: skip

    def __init__(self, **condition: Unpack[ChannelGuestStarSessionEndCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class GuestStarGuestUpdateSubscription(Subscription[ChannelGuestStarGuestUpdate]):
    """Subscription for ``channel.guest_star_guest.update`` (version ``beta``).

    Sends a notification when a guest or a slot is updated in an active Guest Star session.

    .. warning::
        This subscription type is in public beta on Twitch, may change at any time, and should not be used in production.

    .. important::
        Requires the ``channel:read:guest_star``, ``channel:manage:guest_star``, ``moderator:read:guest_star`` or
        ``moderator:manage:guest_star`` scope from the user in ``moderator_user_id``, who must be a moderator of the channel
        or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelGuestStarGuestUpdate
    _version: ClassVar[str] = "beta"
    scopes = ...  # channel:read:guest_star or channel:manage:guest_star or moderator:read:guest_star or moderator:manage:guest_star  # fmt: skip

    def __init__(self, **condition: Unpack[ChannelGuestStarGuestUpdate]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class GuestStarSettingsUpdateSubscription(Subscription[ChannelGuestStarSettingsUpdate]):
    """Subscription for ``channel.guest_star_settings.update`` (version ``beta``).

    Sends a notification when the host's Guest Star preferences are updated.

    .. warning::
        This subscription type is in public beta on Twitch, may change at any time, and should not be used in production.

    .. important::
        Requires the ``channel:read:guest_star``, ``channel:manage:guest_star``, ``moderator:read:guest_star`` or
        ``moderator:manage:guest_star`` scope from the user in ``moderator_user_id``, who must be a moderator of the channel
        or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelGuestStarSettingsUpdate
    _version: ClassVar[str] = "beta"
    scopes = ...  # channel:read:guest_star or channel:manage:guest_star or moderator:read:guest_star or moderator:manage:guest_star  # fmt: skip

    def __init__(self, **condition: Unpack[ChannelGuestStarSettingsUpdate]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelPointsAutoRedeemSubscription(Subscription[ChannelPointsAutomaticRewardRedemptionAddCT]):
    """Subscription for ``channel.channel_points_automatic_reward_redemption.add`` (version ``1``).

    Sends a notification when a viewer redeems an automatic Channel Points reward.

    .. important::
        Requires the ``channel:read:redemptions`` or ``channel:manage:redemptions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChannelPointsAutomaticRewardRedemptionAdd
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:redemptions or channel:manage:redemptions

    def __init__(self, **condition: Unpack[ChannelPointsAutomaticRewardRedemptionAddCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelPointsAutoRedeemV2Subscription(Subscription[ChannelPointsAutomaticRewardRedemptionAddCT]):
    """Subscription for ``channel.channel_points_automatic_reward_redemption.add`` (version ``2``).

    Sends a notification when a viewer redeems an automatic Channel Points reward. Version 2 of this type, with an updated
    event payload.

    .. important::
        Requires the ``channel:read:redemptions`` or ``channel:manage:redemptions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChannelPointsAutomaticRewardRedemptionAdd
    _version: ClassVar[str] = "2"
    scopes = ...  # channel:read:redemptions or channel:manage:redemptions

    def __init__(self, **condition: Unpack[ChannelPointsAutomaticRewardRedemptionAddCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelPointsRewardAddSubscription(Subscription[ChannelPointsCustomRewardAddCT]):
    """Subscription for ``channel.channel_points_custom_reward.add`` (version ``1``).

    Sends a notification when a custom Channel Points reward is created.

    .. important::
        Requires the ``channel:read:redemptions`` or ``channel:manage:redemptions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChannelPointsCustomRewardAdd
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:redemptions or channel:manage:redemptions

    def __init__(self, **condition: Unpack[ChannelPointsCustomRewardAddCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelPointsRewardUpdateSubscription(Subscription[ChannelPointsCustomRewardUpdateCT]):
    """Subscription for ``channel.channel_points_custom_reward.update`` (version ``1``).

    Sends a notification when a custom Channel Points reward is updated.

    .. important::
        Requires the ``channel:read:redemptions`` or ``channel:manage:redemptions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    reward_id: str
        Optional. The ID of a specific reward to receive events for. If omitted, events for all rewards are sent.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChannelPointsCustomRewardUpdate
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:redemptions or channel:manage:redemptions

    def __init__(self, **condition: Unpack[ChannelPointsCustomRewardUpdateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelPointsRewardRemoveSubscription(Subscription[ChannelPointsCustomRewardRemoveCT]):
    """Subscription for ``channel.channel_points_custom_reward.remove`` (version ``1``).

    Sends a notification when a custom Channel Points reward is removed.

    .. important::
        Requires the ``channel:read:redemptions`` or ``channel:manage:redemptions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    reward_id: str
        Optional. The ID of a specific reward to receive events for. If omitted, events for all rewards are sent.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChannelPointsCustomRewardRemove
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:redemptions or channel:manage:redemptions

    def __init__(self, **condition: Unpack[ChannelPointsCustomRewardRemoveCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelPointsRedeemAddSubscription(Subscription[ChannelPointsCustomRewardRedemptionAddCT]):
    """Subscription for ``channel.channel_points_custom_reward_redemption.add`` (version ``1``).

    Sends a notification when a viewer redeems a custom Channel Points reward.

    .. important::
        Requires the ``channel:read:redemptions`` or ``channel:manage:redemptions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    reward_id: str
        Optional. The ID of a specific reward to receive events for. If omitted, events for all rewards are sent.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChannelPointsCustomRewardRedemptionAdd
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:redemptions or channel:manage:redemptions

    def __init__(self, **condition: Unpack[ChannelPointsCustomRewardRedemptionAddCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelPointsRedeemUpdateSubscription(Subscription[ChannelPointsCustomRewardRedemptionUpdateCT]):
    """Subscription for ``channel.channel_points_custom_reward_redemption.update`` (version ``1``).

    Sends a notification when a redemption of a custom Channel Points reward is updated, for example when it is fulfilled or
    cancelled.

    .. important::
        Requires the ``channel:read:redemptions`` or ``channel:manage:redemptions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    reward_id: str
        Optional. The ID of a specific reward to receive events for. If omitted, events for all rewards are sent.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelChannelPointsCustomRewardRedemptionUpdate
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:redemptions or channel:manage:redemptions

    def __init__(self, **condition: Unpack[ChannelPointsCustomRewardRedemptionUpdateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class CustomPowerupRedeemAddSubscription(Subscription[ChannelCustomPowerUpRedemptionAddCT]):
    """Subscription for ``channel.custom_power_up_redemption.add`` (version ``1``).

    Sends a notification when a viewer redeems a custom Power-up in the channel.

    .. important::
        Requires the ``bits:read`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    reward_id: str
        Optional. The ID of a specific custom Power-up to receive events for. If omitted, events for all custom Power-ups are
        sent.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelCustomPowerupRedemptionAdd
    _version: ClassVar[str] = "1"
    scopes = ...  # bits:read

    def __init__(self, **condition: Unpack[ChannelCustomPowerUpRedemptionAddCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelPollBeginSubscription(Subscription[ChannelPollBeginCT]):
    """Subscription for ``channel.poll.begin`` (version ``1``).

    Sends a notification when a poll starts in the channel.

    .. important::
        Requires the ``channel:read:polls`` or ``channel:manage:polls`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelPollBegin
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:polls or channel:manage:polls

    def __init__(self, **condition: Unpack[ChannelPollBeginCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelPollProgressSubscription(Subscription[ChannelPollProgressCT]):
    """Subscription for ``channel.poll.progress`` (version ``1``).

    Sends a notification when users respond to a poll in the channel.

    .. important::
        Requires the ``channel:read:polls`` or ``channel:manage:polls`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelPollProgress
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:polls or channel:manage:polls

    def __init__(self, **condition: Unpack[ChannelPollProgressCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelPollEndSubscription(Subscription[ChannelPollEndCT]):
    """Subscription for ``channel.poll.end`` (version ``1``).

    Sends a notification when a poll ends in the channel.

    .. important::
        Requires the ``channel:read:polls`` or ``channel:manage:polls`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelPollEnd
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:polls or channel:manage:polls

    def __init__(self, **condition: Unpack[ChannelPollEndCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelPredictionBeginSubscription(Subscription[ChannelPredictionBeginCT]):
    """Subscription for ``channel.prediction.begin`` (version ``1``).

    Sends a notification when a Prediction starts in the channel.

    .. important::
        Requires the ``channel:read:predictions`` or ``channel:manage:predictions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelPredictionBegin
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:predictions or channel:manage:predictions

    def __init__(self, **condition: Unpack[ChannelPredictionBeginCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelPredictionProgressSubscription(Subscription[ChannelPredictionProgressCT]):
    """Subscription for ``channel.prediction.progress`` (version ``1``).

    Sends a notification when users participate in a Prediction in the channel.

    .. important::
        Requires the ``channel:read:predictions`` or ``channel:manage:predictions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelPredictionProgress
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:predictions or channel:manage:predictions

    def __init__(self, **condition: Unpack[ChannelPredictionProgressCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelPredictionLockSubscription(Subscription[ChannelPredictionLockCT]):
    """Subscription for ``channel.prediction.lock`` (version ``1``).

    Sends a notification when a Prediction is locked in the channel.

    .. important::
        Requires the ``channel:read:predictions`` or ``channel:manage:predictions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelPredictionLock
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:predictions or channel:manage:predictions

    def __init__(self, **condition: Unpack[ChannelPredictionLockCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelPredictionEndSubscription(Subscription[ChannelPredictionEndCT]):
    """Subscription for ``channel.prediction.end`` (version ``1``).

    Sends a notification when a Prediction ends in the channel.

    .. important::
        Requires the ``channel:read:predictions`` or ``channel:manage:predictions`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelPredictionEnd
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:predictions or channel:manage:predictions

    def __init__(self, **condition: Unpack[ChannelPredictionEndCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class SuspiciousUserMessageSubscription(Subscription[ChannelSuspiciousUserMessageCT]):
    """Subscription for ``channel.suspicious_user.message`` (version ``1``).

    Sends a notification when a user marked as suspicious sends a chat message.

    .. important::
        Requires the ``moderator:read:suspicious_users`` scope from the user in ``moderator_user_id``, who must be a
        moderator of the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelSuspiciousUserMessage
    _version: ClassVar[str] = "1"
    scopes = ...  # moderator:read:suspicious_users

    def __init__(self, **condition: Unpack[ChannelSuspiciousUserMessageCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class SuspiciousUserUpdateSubscription(Subscription[ChannelSuspiciousUserUpdateCT]):
    """Subscription for ``channel.suspicious_user.update`` (version ``1``).

    Sends a notification when a suspicious user is updated.

    .. important::
        Requires the ``moderator:read:suspicious_users`` scope from the user in ``moderator_user_id``, who must be a
        moderator of the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelSuspiciousUserUpdate
    _version: ClassVar[str] = "1"
    scopes = ...  # moderator:read:suspicious_users

    def __init__(self, **condition: Unpack[ChannelSuspiciousUserUpdateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelVIPAddSubscription(Subscription[ChannelVIPAddCT]):
    """Subscription for ``channel.vip.add`` (version ``1``).

    Sends a notification when a VIP is added to the channel.

    .. important::
        Requires the ``channel:read:vips`` or ``channel:manage:vips`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelVipAdd
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:vips or channel:manage:vips

    def __init__(self, **condition: Unpack[ChannelVIPAddCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelVIPRemoveSubscription(Subscription[ChannelVIPRemoveCT]):
    """Subscription for ``channel.vip.remove`` (version ``1``).

    Sends a notification when a VIP is removed from the channel.

    .. important::
        Requires the ``channel:read:vips`` or ``channel:manage:vips`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelVipRemove
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:vips or channel:manage:vips

    def __init__(self, **condition: Unpack[ChannelVIPRemoveCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelWarningAcknowledgementSubscription(Subscription[ChannelWarningAcknowledgeCT]):
    """Subscription for ``channel.warning.acknowledge`` (version ``1``).

    Sends a notification when a user acknowledges a warning. Broadcasters and moderators can see the warning's details.

    .. important::
        Requires the ``moderator:read:warnings`` or ``moderator:manage:warnings`` scope from the user in
        ``moderator_user_id``, who must be a moderator of the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelWarningAcknowledgement
    _version: ClassVar[str] = "1"
    scopes = ...  # moderator:read:warnings or moderator:manage:warnings

    def __init__(self, **condition: Unpack[ChannelWarningAcknowledgeCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ChannelWarningSendSubscription(Subscription[ChannelWarningSendCT]):
    """Subscription for ``channel.warning.send`` (version ``1``).

    Sends a notification when a user is sent a warning. Broadcasters and moderators can see the warning's details.

    .. important::
        Requires the ``moderator:read:warnings`` or ``moderator:manage:warnings`` scope from the user in
        ``moderator_user_id``, who must be a moderator of the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelWarningSend
    _version: ClassVar[str] = "1"
    scopes = ...  # moderator:read:warnings or moderator:manage:warnings

    def __init__(self, **condition: Unpack[ChannelWarningSendCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class CharityDonationSubscription(Subscription[CharityDonationCT]):
    """Subscription for ``channel.charity_campaign.donate`` (version ``1``).

    Sends a notification when a user donates to the broadcaster's charity campaign.

    .. important::
        Requires the ``channel:read:charity`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelCharityCampaignDonate
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:charity

    def __init__(self, **condition: Unpack[CharityDonationCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class CharityCampaignStartSubscription(Subscription[CharityCampaignStartCT]):
    """Subscription for ``channel.charity_campaign.start`` (version ``1``).

    Sends a notification when the broadcaster starts a charity campaign.

    .. important::
        Requires the ``channel:read:charity`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelCharityCampaignStart
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:charity

    def __init__(self, **condition: Unpack[CharityCampaignStartCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class CharityCampaignProgressSubscription(Subscription[CharityCampaignProgressCT]):
    """Subscription for ``channel.charity_campaign.progress`` (version ``1``).

    Sends a notification when progress is made towards the charity campaign's goal, or when the broadcaster changes the
    fundraising goal.

    .. important::
        Requires the ``channel:read:charity`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelCharityCampaignProgress
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:charity

    def __init__(self, **condition: Unpack[CharityCampaignProgressCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class CharityCampaignStopSubscription(Subscription[CharityCampaignStopCT]):
    """Subscription for ``channel.charity_campaign.stop`` (version ``1``).

    Sends a notification when the broadcaster stops a charity campaign.

    .. important::
        Requires the ``channel:read:charity`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelCharityCampaignStop
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:charity

    def __init__(self, **condition: Unpack[CharityCampaignStopCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ConduitShardDisabledSubscription(Subscription[ConduitShardDisabledCT]):
    """Subscription for ``conduit.shard.disabled`` (version ``1``).

    Sends a notification when EventSub disables a shard because the status of its underlying transport changed.

    .. important::
        Requires an app access token. App access tokens can't be used with WebSocket transports, so subscribe over a webhook
        or conduit.

    Parameters
    ----------
    client_id: str
        Your application's client ID. Must match the client ID in the app access token.
    conduit_id: str
        Optional. The ID of the conduit to receive events for. If omitted, events for all of this client's conduits are sent.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ConduitShardDisabled
    _version: ClassVar[str] = "1"
    scopes = ...  # No scopes; requires an app access token

    def __init__(self, **condition: Unpack[ConduitShardDisabledCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class DropEntitlementGrantSubscription(Subscription[DropEntitlementGrantCT]):
    """Subscription for ``drop.entitlement.grant`` (version ``1``).

    Sends a notification when an entitlement for a Drop is granted to a user.

    .. important::
        Requires an app access token. App access tokens can't be used with WebSocket transports, so subscribe over a webhook
        or conduit. Twitch requires batching for this type, so ``is_batching_enabled`` is always sent as ``true``.

    Parameters
    ----------
    organization_id: str
        The ID of the organization that owns the game on the developer portal.
    category_id: str
        Optional. The category (game) ID to receive entitlement notifications for. If omitted, events for all of the
        organization's games are sent.
    campaign_id: str
        Optional. The ID of a specific campaign to receive entitlement notifications for. If omitted, events for all
        campaigns are sent.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.DropEntitlementGrant
    _version: ClassVar[str] = "1"
    scopes = ...  # No scopes; requires an app access token

    def __init__(self, **condition: Unpack[DropEntitlementGrantCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)

        # Twitch rejects drop.entitlement.grant subscriptions that don't enable batching.
        data: dict[str, Any] = self._data
        data["is_batching_enabled"] = True


class ExtensionBitsTransactionCreateSubscription(Subscription[ExtensionBitsTransactionCreateCT]):
    """Subscription for ``extension.bits_transaction.create`` (version ``1``).

    Sends a notification when a Bits transaction occurs for the specified Twitch Extension.

    .. important::
        Requires an app access token. App access tokens can't be used with WebSocket transports, so subscribe over a webhook
        or conduit. The token must belong to the Extension's client ID.

    Parameters
    ----------
    extension_client_id: str
        The client ID of the Extension to receive Bits transactions for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ExtensionBitsTransactionCreate
    _version: ClassVar[str] = "1"
    scopes = ...  # No scopes; requires an app access token

    def __init__(self, **condition: Unpack[ExtensionBitsTransactionCreateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class GoalBeginSubscription(Subscription[GoalsCT]):
    """Subscription for ``channel.goal.begin`` (version ``1``).

    Sends a notification when the broadcaster begins a goal.

    .. important::
        Requires the ``channel:read:goals`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelGoalBegin
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:goals

    def __init__(self, **condition: Unpack[GoalsCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class GoalProgressSubscription(Subscription[GoalsCT]):
    """Subscription for ``channel.goal.progress`` (version ``1``).

    Sends a notification when progress, positive or negative, is made towards the broadcaster's goal.

    .. important::
        Requires the ``channel:read:goals`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelGoalProgress
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:goals

    def __init__(self, **condition: Unpack[GoalsCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class GoalEndSubscription(Subscription[GoalsCT]):
    """Subscription for ``channel.goal.end`` (version ``1``).

    Sends a notification when the broadcaster ends a goal.

    .. important::
        Requires the ``channel:read:goals`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelGoalEnd
    _version: ClassVar[str] = "1"
    scopes = ...  # channel:read:goals

    def __init__(self, **condition: Unpack[GoalsCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class HypeTrainBeginSubscription(Subscription[HypeTrainBeginCT]):
    """Subscription for ``channel.hype_train.begin`` (version ``2``).

    Sends a notification when a Hype Train begins in the channel.

    .. important::
        Requires the ``channel:read:hype_train`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelHypeTrainBegin
    _version: ClassVar[str] = "2"
    scopes = ...  # channel:read:hype_train

    def __init__(self, **condition: Unpack[HypeTrainBeginCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class HypeTrainProgressSubscription(Subscription[HypeTrainProgressCT]):
    """Subscription for ``channel.hype_train.progress`` (version ``2``).

    Sends a notification when a Hype Train makes progress in the channel.

    .. important::
        Requires the ``channel:read:hype_train`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelHypeTrainProgress
    _version: ClassVar[str] = "2"
    scopes = ...  # channel:read:hype_train

    def __init__(self, **condition: Unpack[HypeTrainProgressCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class HypeTrainEndSubscription(Subscription[HypeTrainEndCT]):
    """Subscription for ``channel.hype_train.end`` (version ``2``).

    Sends a notification when a Hype Train ends in the channel.

    .. important::
        Requires the ``channel:read:hype_train`` scope from the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelHypeTrainEnd
    _version: ClassVar[str] = "2"
    scopes = ...  # channel:read:hype_train

    def __init__(self, **condition: Unpack[HypeTrainEndCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ShieldModeBeginSubscription(Subscription[ShieldModeBeginCT]):
    """Subscription for ``channel.shield_mode.begin`` (version ``1``).

    Sends a notification when the broadcaster activates Shield Mode.

    .. important::
        Requires the ``moderator:read:shield_mode`` or ``moderator:manage:shield_mode`` scope from the user in
        ``moderator_user_id``, who must be a moderator of the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelShieldModeBegin
    _version: ClassVar[str] = "1"
    scopes = ...  # moderator:read:shield_mode or moderator:manage:shield_mode

    def __init__(self, **condition: Unpack[ShieldModeBeginCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ShieldModeEndSubscription(Subscription[ShieldModeEndCT]):
    """Subscription for ``channel.shield_mode.end`` (version ``1``).

    Sends a notification when the broadcaster deactivates Shield Mode.

    .. important::
        Requires the ``moderator:read:shield_mode`` or ``moderator:manage:shield_mode`` scope from the user in
        ``moderator_user_id``, who must be a moderator of the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelShieldModeEnd
    _version: ClassVar[str] = "1"
    scopes = ...  # moderator:read:shield_mode or moderator:manage:shield_mode

    def __init__(self, **condition: Unpack[ShieldModeEndCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ShoutoutCreateSubscription(Subscription[ShoutoutCreateCT]):
    """Subscription for ``channel.shoutout.create`` (version ``1``).

    Sends a notification when the broadcaster sends a Shoutout.

    .. important::
        Requires the ``moderator:read:shoutouts`` or ``moderator:manage:shoutouts`` scope from the user in
        ``moderator_user_id``, who must be a moderator of the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelShoutoutCreate
    _version: ClassVar[str] = "1"
    scopes = ...  # moderator:read:shoutouts or moderator:manage:shoutouts

    def __init__(self, **condition: Unpack[ShoutoutCreateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class ShoutoutReceiveSubscription(Subscription[ShoutoutReceiveCT]):
    """Subscription for ``channel.shoutout.receive`` (version ``1``).

    Sends a notification when the broadcaster receives a Shoutout.

    .. important::
        Requires the ``moderator:read:shoutouts`` or ``moderator:manage:shoutouts`` scope from the user in
        ``moderator_user_id``, who must be a moderator of the channel or the broadcaster.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    moderator_user_id: str
        The ID of a moderator of the channel, or the broadcaster, to subscribe as. With a user access token this must match
        the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.ChannelShoutoutReceive
    _version: ClassVar[str] = "1"
    scopes = ...  # moderator:read:shoutouts or moderator:manage:shoutouts

    def __init__(self, **condition: Unpack[ShoutoutReceiveCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class StreamOnlineSubscription(Subscription[StreamOnlineCT]):
    """Subscription for ``stream.online`` (version ``1``).

    Sends a notification when the broadcaster starts a stream.

    .. important::
        No authorization required.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.StreamOnline
    _version: ClassVar[str] = "1"
    scopes = ...  # No scopes required

    def __init__(self, **condition: Unpack[StreamOnlineCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class StreamOfflineSubscription(Subscription[StreamOfflineCT]):
    """Subscription for ``stream.offline`` (version ``1``).

    Sends a notification when the broadcaster stops a stream.

    .. important::
        No authorization required.

    Parameters
    ----------
    broadcaster_user_id: str
        The ID of the broadcaster (channel) to receive events for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.StreamOffline
    _version: ClassVar[str] = "1"
    scopes = ...  # No scopes required

    def __init__(self, **condition: Unpack[StreamOfflineCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class UserAuthorizationGrantSubscription(Subscription[UserAuthorizationGrantCT]):
    """Subscription for ``user.authorization.grant`` (version ``1``).

    Sends a notification when a user grants authorization to your application.

    .. important::
        Requires an app access token. App access tokens can't be used with WebSocket transports, so subscribe over a webhook
        or conduit.

    Parameters
    ----------
    client_id: str
        Your application's client ID. Must match the client ID in the app access token.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.UserAuthorizationGrant
    _version: ClassVar[str] = "1"
    scopes = ...  # No scopes; requires an app access token

    def __init__(self, **condition: Unpack[UserAuthorizationGrantCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class UserAuthorizationRevokeSubscription(Subscription[UserAuthorizationRevokeCT]):
    """Subscription for ``user.authorization.revoke`` (version ``1``).

    Sends a notification when a user revokes your application's authorization.

    .. important::
        Requires an app access token. App access tokens can't be used with WebSocket transports, so subscribe over a webhook
        or conduit.

    Parameters
    ----------
    client_id: str
        Your application's client ID. Must match the client ID in the app access token.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.UserAuthorizationRevoke
    _version: ClassVar[str] = "1"
    scopes = ...  # No scopes; requires an app access token

    def __init__(self, **condition: Unpack[UserAuthorizationRevokeCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class UserUpdateSubscription(Subscription[UserUpdateCT]):
    """Subscription for ``user.update`` (version ``1``).

    Sends a notification when a user updates their account.

    .. important::
        No authorization required. If the user has granted the ``user:read:email`` scope, the notification also includes
        their email address.

    Parameters
    ----------
    user_id: str
        The ID of the user to receive account updates for.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.UserUpdate
    _version: ClassVar[str] = "1"
    scopes = ...  # No scopes required (user:read:email adds the email field)

    def __init__(self, **condition: Unpack[UserUpdateCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)


class WhisperReceivedSubscription(Subscription[WhisperReceivedCT]):
    """Subscription for ``user.whisper.message`` (version ``1``).

    Sends a notification when the user in ``user_id`` receives a whisper.

    .. important::
        Requires the ``user:read:whispers`` or ``user:manage:whispers`` scope from the user in ``user_id``.

    Parameters
    ----------
    user_id: str
        The ID of the user receiving whispers. With a user access token this must match the token's user.
    """

    _type: ClassVar[SubscriptionType] = SubscriptionType.UserWhisperMessage
    _version: ClassVar[str] = "1"
    scopes = ...  # user:read:whispers or user:manage:whispers

    def __init__(self, **condition: Unpack[WhisperReceivedCT]) -> None:
        super().__init__(condition=condition, type=self._type, version=self._version)
