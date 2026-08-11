"""
MIT License

Copyright (c) 2017 - Present TwitchIO, PythonistaGuild

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

from typing import Any, Generic, Literal, NotRequired, TypeAlias, TypedDict, TypeVar

from .conduits import Condition, ConduitData, ShardData
from .eventsub import ChatMessageData


__all__ = (
    "AdScheduleResponse",
    "AdScheduleResponseData",
    "AuthorizationByUserResponse",
    "AuthorizationByUserResponseData",
    "AuthorizationURLResponse",
    "BitsLeaderboardResponse",
    "ChannelChatBadgesResponseData",
    "ChannelChatBadgesResponseVersions",
    "ChannelEditorsResponse",
    "ChannelEditorsResponse",
    "ChannelEditorsResponseData",
    "ChannelEmotesResponse",
    "ChannelFollowersResponseData",
    "ChannelInformationResponse",
    "ChannelInformationResponseData",
    "ChannelTeamsResponseData",
    "CheermotesResponse",
    "CheermotesResponseData",
    "CheermotesResponseTiers",
    "ClientCredentialsResponse",
    "ClipsResponseData",
    "ConduitPayload",
    "ContentClassificationLabelData",
    "ContentClassificationLabelsResponse",
    "CustomPowerupResponseData",
    "CustomPowerupResponseImage",
    "EventsubSubscriptionResponse",
    "EventsubSubscriptionResponseData",
    "ExtensionAnalyticsResponse",
    "ExtensionTransactionsResponse",
    "ExtensionTransactionsResponseCost",
    "ExtensionTransactionsResponseData",
    "ExtensionTransactionsResponseProductData",
    "FollowedChannelsResponseData",
    "GameAnalyticsResponse",
    "GamesResponse",
    "GamesResponseData",
    "GlobalChatBadgesResponse",
    "GlobalChatBadgesResponseData",
    "GlobalChatBadgesResponseVersions",
    "GlobalEmotesResponse",
    "GlobalEmotesResponseData",
    "HypeTrainEventsResponse",
    "HypeTrainStatusResponse",
    "HypeTrainStatusResponseData",
    "HypeTrainStatusTopContributions",
    "OAuthResponses",
    "PinnedChatMessageData",
    "PinnedChatMessageResponse",
    "RawResponse",
    "RefreshTokenResponse",
    "SearchChannelsResponseData",
    "ShardPayload",
    "SharedChatSessionResponse",
    "SharedChatSessionResponseData",
    "SnoozeNextAdResponse",
    "StartCommercialResponse",
    "StartCommercialResponseData",
    "StreamsResponseData",
    "SuspiciousChatUserResponse",
    "TeamsResponseData",
    "TopGamesResponseData",
    "UserChatColorResponse",
    "UserChatColorResponseData",
    "UserTokenResponse",
    "ValidateTokenResponse",
    "VideosResponseData",
    "WarnChatUserResponse",
    "WarnChatUserResponseData",
)

T = TypeVar("T")


class Payload(TypedDict, Generic[T]):
    data: list[T]


class _TokenResponseBase(TypedDict):
    access_token: str
    refresh_token: str
    expires_in: int
    scope: str | list[str]
    token_type: str


RefreshTokenResponse: TypeAlias = _TokenResponseBase
UserTokenResponse: TypeAlias = _TokenResponseBase


class _MaxPerStreamSetting(TypedDict):
    is_enabled: bool
    max_per_stream: int


class _MaxPerUserPerStreamSetting(TypedDict):
    is_enabled: bool
    max_per_user_per_stream: int


class _GlobalCooldownSetting(TypedDict):
    is_enabled: bool
    global_cooldown_seconds: int


class _ImageUrlSizes(TypedDict):
    url_1x: str
    url_2x: str
    url_4x: str


class ValidateTokenResponse(TypedDict):
    client_id: str
    login: str
    scopes: list[str]
    user_id: str
    expires_in: int


class ClientCredentialsResponse(TypedDict):
    access_token: str
    expires_in: int
    token_type: str


class AuthorizationURLResponse(TypedDict):
    url: str
    client_id: str
    redirect_uri: str
    response_type: str
    scopes: list[str]
    force_verify: bool
    state: str


class DeviceCodeFlowResponse(TypedDict):
    device_code: str
    expires_in: int
    interval: int
    user_code: str
    verification_uri: str


class DeviceCodeTokenResponse(TypedDict):
    access_token: str
    expires_in: int
    refresh_token: str
    scope: list[str]
    token_type: str


OAuthResponses: TypeAlias = (
    RefreshTokenResponse | ValidateTokenResponse | ClientCredentialsResponse | UserTokenResponse | AuthorizationURLResponse
)
RawResponse: TypeAlias = dict[str, Any]


class Pagination(TypedDict):
    cursor: str | None


class DateRange(TypedDict):
    started_at: str
    ended_at: str


class StartCommercialResponseData(TypedDict):
    length: int
    message: str
    retry_after: int


class StartCommercialResponse(Payload[StartCommercialResponseData]):
    pass


class AdScheduleResponseData(TypedDict):
    snooze_count: int
    snooze_refresh_at: str
    next_ad_at: str
    duration: int
    last_ad_at: str
    preroll_free_time: int


class AdScheduleResponse(Payload[AdScheduleResponseData]):
    pass


class SnoozeNextAdResponseData(TypedDict):
    snooze_count: int
    snooze_refresh_at: str
    next_ad_at: str


class SnoozeNextAdResponse(Payload[SnoozeNextAdResponseData]):
    pass


class ExtensionAnalyticsResponseData(TypedDict):
    extension_id: str
    URL: str
    type: str
    date_range: DateRange


class ExtensionAnalyticsResponse(Payload[ExtensionAnalyticsResponseData]):
    pagination: Pagination


class GameAnalyticsResponseData(TypedDict):
    game_id: str
    URL: str
    type: str
    date_range: DateRange


class GameAnalyticsResponse(Payload[GameAnalyticsResponseData]):
    pagination: Pagination


class BitsLeaderboardResponseData(TypedDict):
    user_id: str
    user_login: str
    user_name: str
    rank: int
    score: int


class BitsLeaderboardResponse(Payload[BitsLeaderboardResponseData]):
    date_range: DateRange
    total: int


class CheermotesResponseTiers(TypedDict):
    min_bits: int
    id: str
    color: str
    images: dict[str, dict[str, dict[str, str]]]
    can_cheer: bool
    show_in_bits_card: bool


class CheermotesResponseData(TypedDict):
    prefix: str
    tiers: list[CheermotesResponseTiers]
    type: str
    order: int
    last_updated: str
    is_charitable: bool


class CheermotesResponse(Payload[CheermotesResponseData]):
    pass


class ExtensionTransactionsResponseCost(TypedDict):
    amount: int
    type: str


class ExtensionTransactionsResponseProductData(TypedDict):
    sku: str
    domain: str
    cost: ExtensionTransactionsResponseCost
    inDevelopment: bool
    displayName: str
    expiration: str
    broadcast: bool


class ExtensionTransactionsResponseData(TypedDict):
    id: str
    timestamp: str
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    user_id: str
    user_login: str
    user_name: str
    product_type: str
    product_data: ExtensionTransactionsResponseProductData


class ExtensionTransactionsResponse(Payload[ExtensionTransactionsResponseData]):
    pagination: Pagination


class ChannelInformationResponseData(TypedDict):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    broadcaster_language: str
    game_name: str
    game_id: str
    title: str
    delay: int
    tags: list[str]
    content_classification_labels: list[str]
    is_branded_content: bool


class ChannelInformationResponse(Payload[ChannelInformationResponseData]):
    pass


class ChannelEditorsResponseData(TypedDict):
    user_id: str
    user_name: str
    created_at: str


class ChannelEditorsResponse(Payload[ChannelEditorsResponseData]):
    pass


class FollowedChannelsResponseData(TypedDict):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    followed_at: str


class FollowedChannelsResponse(Payload[FollowedChannelsResponseData]):
    pagination: Pagination
    total: int


class ChannelFollowersResponseData(TypedDict):
    followed_at: str
    user_id: str
    user_login: str
    user_name: str


class ChannelFollowersResponse(Payload[ChannelFollowersResponseData]):
    pagination: Pagination
    total: int


class CustomPowerupResponseImage(_ImageUrlSizes): ...


class CustomPowerupResponseDefaultImage(_ImageUrlSizes): ...


class CustomPowerupResponseData(TypedDict):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    id: str
    title: str
    prompt: str
    bits: int
    image: CustomPowerupResponseImage
    default_image: CustomPowerupResponseDefaultImage
    background_color: str
    is_enabled: bool
    is_user_input_required: bool
    max_per_stream_setting: _MaxPerStreamSetting
    max_per_user_stream_setting: _MaxPerUserPerStreamSetting
    global_cooldown_setting: _GlobalCooldownSetting
    is_paused: bool
    is_in_stock: bool
    redemptions_redeemed_current_stream: int | None
    cooldown_expires_at: str | None


class CustomPowerupResponse(Payload[CustomPowerupResponseData]):
    pass


class CustomRewardsResponseImage(_ImageUrlSizes): ...


class CustomRewardsResponseDefaultImage(_ImageUrlSizes): ...


class CustomRewardsResponseMaxPerStreamSetting(_MaxPerStreamSetting): ...


class CustomRewardsResponseMaxPerUserPerStreamSetting(_MaxPerUserPerStreamSetting): ...


class CustomRewardsResponseGlobalCooldownSetting(_GlobalCooldownSetting): ...


class CustomRewardsResponseData(TypedDict):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    id: str
    title: str
    prompt: str
    cost: int
    image: CustomRewardsResponseImage | None
    default_image: CustomRewardsResponseDefaultImage
    background_color: str
    is_enabled: bool
    is_user_input_required: bool
    max_per_stream_setting: CustomRewardsResponseMaxPerStreamSetting
    max_per_user_per_stream_setting: CustomRewardsResponseMaxPerUserPerStreamSetting
    global_cooldown_setting: CustomRewardsResponseGlobalCooldownSetting
    is_paused: bool
    is_in_stock: bool
    should_redemptions_skip_request_queue: bool
    redemptions_redeemed_current_stream: int | None
    cooldown_expires_at: str | None


class CustomRewardsResponse(Payload[CustomRewardsResponseData]):
    pass


class CustomRewardRedemptionResponseReward(TypedDict):
    id: str
    title: str
    prompt: str
    cost: int


class CustomRewardRedemptionResponseData(TypedDict):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    id: str
    user_login: str
    user_id: str
    user_name: str
    user_input: str
    status: Literal["CANCELED", "FULFILLED", "UNFULFILLED"]
    redeemed_at: str
    reward: CustomRewardRedemptionResponseReward


class CustomRewardRedemptionResponse(Payload[CustomRewardRedemptionResponseData]):
    pass


class CharityCampaignResponseCurrentAmount(TypedDict):
    value: int
    decimal_places: int
    currency: str


class CharityCampaignResponseTargetAmount(TypedDict):
    value: int
    decimal_places: int
    currency: str


class CharityCampaignResponseData(TypedDict):
    id: str
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    current_amount: CharityCampaignResponseCurrentAmount
    target_amount: CharityCampaignResponseTargetAmount | None


class CharityCampaignResponse(Payload[CharityCampaignResponseData]):
    pass


class CharityCampaignDonationsResponseAmount(TypedDict):
    value: int
    decimal_places: int
    currency: str


class CharityCampaignDonationsResponseData(TypedDict):
    id: str
    campaign_id: str
    user_id: str
    user_login: str
    user_name: str
    amount: CharityCampaignDonationsResponseAmount


class CharityCampaignDonationsResponse(Payload[CharityCampaignDonationsResponseData]):
    pagination: Pagination


class ChattersResponseData(TypedDict):
    user_id: str
    user_login: str
    user_name: str


class ChattersResponse(Payload[ChattersResponseData]):
    pagination: Pagination
    total: int


class ChannelEmotesResponseImages(_ImageUrlSizes): ...


class ChannelEmotesResponseData(TypedDict):
    id: str
    name: str
    images: ChannelEmotesResponseImages
    tier: Literal["1000", "2000", "3000"]
    emote_type: Literal["bitstier", "follower", "subscriptions"]
    emote_set_id: str
    format: list[str]
    scale: list[str]
    theme_mode: list[str]


class ChannelEmotesResponse(Payload[ChannelEmotesResponseData]):
    template: str


class GlobalEmotesResponseImages(_ImageUrlSizes): ...


class GlobalEmotesResponseData(TypedDict):
    id: str
    name: str
    images: GlobalEmotesResponseImages
    format: list[str]
    scale: list[str]
    theme_mode: list[str]


class GlobalEmotesResponse(Payload[GlobalEmotesResponseData]):
    template: str


class EmoteSetsResponseImages(_ImageUrlSizes): ...


class EmoteSetsResponseData(TypedDict):
    id: str
    name: str
    images: EmoteSetsResponseImages
    emote_type: str
    emote_set_id: str
    owner_id: str
    format: list[str]
    scale: list[str]
    theme_mode: list[str]


class EmoteSetsResponse(Payload[EmoteSetsResponseData]):
    template: str


class ChannelChatBadgesResponseVersions(TypedDict):
    id: str
    image_url_1x: str
    image_url_2x: str
    image_url_4x: str
    title: str
    description: str
    click_action: str | None
    click_url: str | None


class ChannelChatBadgesResponseData(TypedDict):
    set_id: str
    versions: list[ChannelChatBadgesResponseVersions]


class ChannelChatBadgesResponse(Payload[ChannelChatBadgesResponseData]):
    pass


class GlobalChatBadgesResponseVersions(TypedDict):
    id: str
    image_url_1x: str
    image_url_2x: str
    image_url_4x: str
    title: str
    description: str
    click_action: str | None
    click_url: str | None


class GlobalChatBadgesResponseData(TypedDict):
    set_id: str
    versions: list[GlobalChatBadgesResponseVersions]


class GlobalChatBadgesResponse(Payload[GlobalChatBadgesResponseData]):
    pass


class ChatSettingsResponseData(TypedDict):
    broadcaster_id: str
    emote_mode: bool
    follower_mode: bool
    follower_mode_duration: int | None
    moderator_id: str
    non_moderator_chat_delay: bool
    non_moderator_chat_delay_duration: int | None
    slow_mode: bool
    slow_mode_wait_time: int | None
    subscriber_mode: bool
    unique_chat_mode: bool


class ChatSettingsResponse(Payload[ChatSettingsResponseData]):
    pass


class SharedChatParticipantsData(TypedDict):
    broadcaster_id: str


class SharedChatSessionResponseData(TypedDict):
    session_id: str
    host_broadcaster_id: str
    participants: list[SharedChatParticipantsData]
    created_at: str
    updated_at: str


class SharedChatSessionResponse(Payload[SharedChatSessionResponseData]):
    pass


class UserEmotesResponseData(TypedDict):
    id: str
    name: str
    emote_type: str
    emote_set_id: str
    owner_id: str
    format: list[str]
    scale: list[str]
    theme_mode: list[str]


class UserEmotesResponse(Payload[UserEmotesResponseData]):
    template: str
    pagination: Pagination


class SendChatMessageResponseDropReason(TypedDict):
    code: str
    message: str


class SendChatMessageResponseData(TypedDict):
    message_id: str
    is_sent: bool
    drop_reason: SendChatMessageResponseDropReason | None


class SendChatMessageResponse(Payload[SendChatMessageResponseData]):
    pass


class UserChatColorResponseData(TypedDict):
    user_id: str
    user_login: str
    user_name: str
    color: str


class UserChatColorResponse(Payload[UserChatColorResponseData]):
    pass


class CreateClipResponseData(TypedDict):
    edit_url: str
    id: str


class CreateClipResponse(Payload[CreateClipResponseData]):
    pass


class ClipsResponseData(TypedDict):
    id: str
    url: str
    embed_url: str
    broadcaster_id: str
    broadcaster_name: str
    creator_id: str
    creator_name: str
    video_id: str
    game_id: str
    language: str
    title: str
    view_count: int
    created_at: str
    thumbnail_url: str
    duration: float
    vod_offset: int | None
    is_featured: bool


class ClipsResponse(Payload[ClipsResponseData]):
    pagination: Pagination


class ConduitPayload(Payload[ConduitData]):
    pass


class ShardPayload(Payload[ShardData]):
    pass


class ContentClassificationLabelData(TypedDict):
    id: str
    description: str
    name: str


class ContentClassificationLabelsResponse(Payload[ContentClassificationLabelData]):
    pass


class DropsEntitlementsResponseData(TypedDict):
    id: str
    benefit_id: str
    timestamp: str
    user_id: str
    game_id: str
    fulfillment_status: Literal["CLAIMED", "FULFILLED"]
    last_updated: str


class DropsEntitlementsResponse(Payload[DropsEntitlementsResponseData]):
    pagination: Pagination


class UpdateDropsEntitlementsResponseData(TypedDict):
    status: Literal["INVALID_ID", "NOT_FOUND", "SUCCESS", "UNAUTHORIZED", "UPDATE_FAILED"]
    ids: list[str]


class UpdateDropsEntitlementsResponse(Payload[UpdateDropsEntitlementsResponseData]):
    pass


class ExtensionConfigurationSegmentResponseData(TypedDict):
    segment: str
    broadcaster_id: str
    content: str
    version: str


class ExtensionConfigurationSegmentResponse(Payload[ExtensionConfigurationSegmentResponseData]):
    pass


class ExtensionLiveChannelsResponseData(TypedDict):
    broadcaster_id: str
    broadcaster_name: str
    game_name: str
    game_id: str
    title: str


class ExtensionLiveChannelsResponse(Payload[ExtensionLiveChannelsResponseData]):
    pagination: Pagination


class ExtensionSecretsResponseSecrets(TypedDict):
    content: str
    active_at: str
    expires_at: str


class ExtensionSecretsResponseData(TypedDict):
    format_version: int
    secrets: list[ExtensionSecretsResponseSecrets]


class ExtensionSecretsResponse(Payload[ExtensionSecretsResponseData]):
    pass


class CreateExtensionSecretResponseSecrets(TypedDict):
    content: str
    active_at: str
    expires_at: str


class CreateExtensionSecretResponseData(TypedDict):
    format_version: int
    secrets: list[CreateExtensionSecretResponseSecrets]


class CreateExtensionSecretResponse(Payload[CreateExtensionSecretResponseData]):
    pass


class ExtensionsResponseMobile(TypedDict):
    viewer_url: str


class ExtensionsResponsePanel(TypedDict):
    viewer_url: str
    height: int
    can_link_external_content: bool


class ExtensionsResponseVideoOverlay(TypedDict):
    viewer_url: str
    can_link_external_content: bool


class ExtensionsResponseComponent(TypedDict):
    viewer_url: str
    aspect_ratio_x: int
    aspect_ratio_y: int
    autoscale: bool
    scale_pixels: int
    target_height: int
    can_link_external_content: bool


class ExtensionsResponseConfig(TypedDict):
    viewer_url: str
    can_link_external_content: bool


class ExtensionsResponseViews(TypedDict):
    mobile: ExtensionsResponseMobile
    panel: ExtensionsResponsePanel
    video_overlay: ExtensionsResponseVideoOverlay
    component: ExtensionsResponseComponent
    config: ExtensionsResponseConfig


class ExtensionsResponseData(TypedDict):
    author_name: str
    bits_enabled: bool
    can_install: bool
    configuration_location: str
    description: str
    eula_tos_url: str
    has_chat_support: bool
    icon_url: str
    icon_urls: dict[str, str]
    id: str
    name: str
    privacy_policy_url: str
    request_identity_link: bool
    screenshot_urls: list[str]
    state: str
    subscriptions_support_level: str
    summary: str
    support_email: str
    version: str
    viewer_summary: str
    views: ExtensionsResponseViews
    allowlisted_config_urls: list[str]
    allowlisted_panel_urls: list[str]


class ExtensionsResponse(Payload[ExtensionsResponseData]):
    pass


class ReleasedExtensionsResponseMobile(TypedDict):
    viewer_url: str


class ReleasedExtensionsResponsePanel(TypedDict):
    viewer_url: str
    height: int
    can_link_external_content: bool


class ReleasedExtensionsResponseVideoOverlay(TypedDict):
    viewer_url: str
    can_link_external_content: bool


class ReleasedExtensionsResponseComponent(TypedDict):
    viewer_url: str
    aspect_ratio_x: int
    aspect_ratio_y: int
    autoscale: bool
    scale_pixels: int
    target_height: int
    can_link_external_content: bool


class ReleasedExtensionsResponseConfig(TypedDict):
    viewer_url: str
    can_link_external_content: bool


class ReleasedExtensionsResponseViews(TypedDict):
    mobile: ReleasedExtensionsResponseMobile
    panel: ReleasedExtensionsResponsePanel
    video_overlay: ReleasedExtensionsResponseVideoOverlay
    component: ReleasedExtensionsResponseComponent
    config: ReleasedExtensionsResponseConfig


class ReleasedExtensionsResponseData(TypedDict):
    author_name: str
    bits_enabled: bool
    can_install: bool
    configuration_location: str
    description: str
    eula_tos_url: str
    has_chat_support: bool
    icon_url: str
    icon_urls: dict[str, str]
    id: str
    name: str
    privacy_policy_url: str
    request_identity_link: bool
    screenshot_urls: list[str]
    state: str
    subscriptions_support_level: str
    summary: str
    support_email: str
    version: str
    viewer_summary: str
    views: ReleasedExtensionsResponseViews
    allowlisted_config_urls: list[str]
    allowlisted_panel_urls: list[str]


class ReleasedExtensionsResponse(Payload[ReleasedExtensionsResponseData]):
    pass


class ExtensionBitsProductsResponseCost(TypedDict):
    amount: int
    type: str


class ExtensionBitsProductsResponseData(TypedDict):
    sku: str
    cost: ExtensionBitsProductsResponseCost
    in_development: bool
    display_name: str
    expiration: str
    is_broadcast: bool


class ExtensionBitsProductsResponse(Payload[ExtensionBitsProductsResponseData]):
    pass


class UpdateExtensionBitsProductResponseCost(TypedDict):
    amount: int
    type: str


class UpdateExtensionBitsProductResponseData(TypedDict):
    sku: str
    cost: UpdateExtensionBitsProductResponseCost
    in_development: bool
    display_name: str
    expiration: str
    is_broadcast: bool


class UpdateExtensionBitsProductResponse(Payload[UpdateExtensionBitsProductResponseData]):
    pass


class EventsubTransportData(TypedDict):
    method: Literal["websocket", "webhook"]
    callback: NotRequired[str]
    session_id: NotRequired[str]
    connected_at: NotRequired[str]
    disconnected_at: NotRequired[str]


class EventsubSubscriptionResponseData(TypedDict):
    id: str
    status: Literal[
        "enabled",
        "webhook_callback_verification_pending",
        "webhook_callback_verification_failed",
        "notification_failures_exceeded",
        "authorization_revoked",
        "moderator_removed",
        "user_removed",
        "version_removed",
        "beta_maintenance",
        "websocket_disconnected",
        "websocket_failed_ping_pong",
        "websocket_received_inbound_traffic",
        "websocket_connection_unused",
        "websocket_internal_error",
        "websocket_network_timeout",
        "websocket_network_error",
    ]
    type: str
    version: str
    condition: Condition
    created_at: str
    cost: int
    transport: EventsubTransportData


class EventsubSubscriptionResponse(Payload[EventsubSubscriptionResponseData]):
    total: int
    total_cost: int
    max_total_cost: int
    pagination: Pagination


class TopGamesResponseData(TypedDict):
    id: str
    name: str
    box_art_url: str
    igdb_id: str


class TopGamesResponse(Payload[TopGamesResponseData]):
    pagination: Pagination


class GamesResponseData(TypedDict):
    id: str
    name: str
    box_art_url: str
    igdb_id: str


class GamesResponse(Payload[GamesResponseData]):
    pass


class CreatorGoalsResponseData(TypedDict):
    id: str
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    type: Literal[
        "follower",
        "subscription",
        "subscription_count",
        "new_subscription",
        "new_subscription_count",
        "new_bit",
        "new_cheerer",
    ]
    description: str
    current_amount: int
    target_amount: int
    created_at: str


class CreatorGoalsResponse(Payload[CreatorGoalsResponseData]):
    pass


class ChannelGuestStarSettingsResponse(TypedDict):
    is_moderator_send_live_enabled: bool
    slot_count: int
    is_browser_source_audio_enabled: bool
    group_layout: str
    browser_source_token: str


# TODO GUESTS
class GuestStarSessionResponse(TypedDict):
    id: str


class CreateGuestStarSessionResponse(TypedDict): ...


class EndGuestStarSessionResponse(TypedDict): ...


class GuestStarInvitesResponse(TypedDict): ...


class HypeTrainEventsResponseContributions(TypedDict):
    total: int
    type: Literal["BITS", "SUBS", "OTHER"]
    user: str


class HypeTrainEventsResponseEventData(TypedDict):
    broadcaster_id: str
    cooldown_end_time: str
    expires_at: str
    goal: int
    id: str
    last_contribution: HypeTrainEventsResponseContributions
    level: int
    started_at: str
    top_contributions: list[HypeTrainEventsResponseContributions]
    total: int


class HypeTrainEventsResponseData(TypedDict):
    id: str
    event_type: str
    event_timestamp: str
    version: str
    event_data: HypeTrainEventsResponseEventData


class HypeTrainEventsResponse(Payload[HypeTrainEventsResponseData]):
    pagination: Pagination


class HypeTrainStatusTopContributions(TypedDict):
    user_id: str
    user_login: str
    user_name: str
    type: Literal["bits", "subscriptions", "other"]
    total: int


class HypeTrainStatusSharedParticipantsData(TypedDict):
    broadcaster_user_id: str
    broadcaster_user_login: str
    broadcaster_user_name: str


class HypeTrainStatusAllTimeHighData(TypedDict):
    level: int
    total: int
    achieved_at: str


class HypeTrainStatusCurrentData(TypedDict):
    id: str
    broadcaster_user_id: str
    broadcaster_user_login: str
    broadcaster_user_name: str
    level: int
    total: int
    progress: int
    goal: int
    top_contributions: list[HypeTrainStatusTopContributions]
    shared_train_participants: list[HypeTrainStatusSharedParticipantsData]
    started_at: str
    expires_at: str
    type: Literal["treasure", "golden_kappa", "regular"]
    is_shared_train: bool


class HypeTrainStatusResponseData(TypedDict):
    current: HypeTrainStatusCurrentData | None
    all_time_high: HypeTrainStatusAllTimeHighData | None
    shared_all_time_high: HypeTrainStatusAllTimeHighData | None


class HypeTrainStatusResponse(Payload[HypeTrainStatusResponseData]):
    pass


class CheckAutomodStatusResponseData(TypedDict):
    msg_id: str
    is_permitted: bool


class CheckAutomodStatusResponse(Payload[CheckAutomodStatusResponseData]):
    pass


class AutomodSettingsResponseData(TypedDict):
    broadcaster_id: str
    moderator_id: str
    overall_level: int | None
    disability: int
    aggression: int
    sexuality_sex_or_gender: int
    misogyny: int
    bullying: int
    swearing: int
    race_ethnicity_or_religion: int
    sex_based_terms: int


class AutomodSettingsResponse(Payload[AutomodSettingsResponseData]):
    pass


class UpdateAutomodSettingsResponseData(TypedDict):
    broadcaster_id: str
    moderator_id: str
    overall_level: int | None
    disability: int
    aggression: int
    sexuality_sex_or_gender: int
    misogyny: int
    bullying: int
    swearing: int
    race_ethnicity_or_religion: int
    sex_based_terms: int


class UpdateAutomodSettingsResponse(Payload[UpdateAutomodSettingsResponseData]):
    pass


class BannedUsersResponseData(TypedDict):
    user_id: str
    user_login: str
    user_name: str
    expires_at: str
    created_at: str
    reason: str
    moderator_id: str
    moderator_login: str
    moderator_name: str


class BannedUsersResponse(Payload[BannedUsersResponseData]):
    pagination: Pagination


class BanUserResponseData(TypedDict):
    broadcaster_id: str
    moderator_id: str
    user_id: str
    created_at: str
    end_time: str | None


class BanUserResponse(Payload[BanUserResponseData]):
    pass


class UnbanRequestsResponseData(TypedDict):
    id: str
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    moderator_id: str
    moderator_login: str
    moderator_name: str
    user_id: str
    user_login: str
    user_name: str
    text: str
    status: Literal["pending", "approved", "denied", "acknowledged", "canceled"]
    created_at: str
    resolved_at: str
    resolution_text: str


class UnbanRequestsResponse(Payload[UnbanRequestsResponseData]):
    pagination: Pagination


class ResolveUnbanRequestsResponseData(TypedDict):
    id: str
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    moderator_id: str
    moderator_login: str
    moderator_name: str
    user_id: str
    user_login: str
    user_name: str
    text: str
    status: Literal["approved", "denied"]
    created_at: str
    resolved_at: str
    resolution_text: str


class ResolveUnbanRequestsResponse(Payload[ResolveUnbanRequestsResponseData]):
    pass


class BlockedTermsResponseData(TypedDict):
    broadcaster_id: str
    moderator_id: str
    id: str
    text: str
    created_at: str
    updated_at: str
    expires_at: str | None


class BlockedTermsResponse(Payload[BlockedTermsResponseData]):
    pagination: Pagination


class AddBlockedTermResponse(Payload[BlockedTermsResponseData]):
    pass


class ModeratedChannelsResponseData(TypedDict):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str


class ModeratedChannelsResponse(Payload[ModeratedChannelsResponseData]):
    pagination: Pagination


class ModeratorsResponseData(TypedDict):
    user_id: str
    user_login: str
    user_name: str


class ModeratorsResponse(Payload[ModeratorsResponseData]):
    pagination: Pagination


class VipsResponseData(TypedDict):
    user_id: str
    user_name: str
    user_login: str


class VipsResponse(Payload[VipsResponseData]):
    pagination: Pagination


class ShieldModeStatusResponseData(TypedDict):
    is_active: bool
    moderator_id: str
    moderator_login: str
    moderator_name: str
    last_activated_at: str


class UpdateShieldModeStatusResponse(Payload[ShieldModeStatusResponseData]):
    pass


class ShieldModeStatusResponse(Payload[ShieldModeStatusResponseData]):
    pass


class PinnedChatMessageData(TypedDict):
    message_id: str
    broadcaster_id: str
    sender_user_id: str
    sender_user_login: str
    sender_user_name: str
    pinned_by_user_id: str
    pinned_by_user_login: str
    pinned_by_user_name: str
    message: ChatMessageData
    starts_at: str
    ends_at: str
    updated_at: str


class PinnedChatMessageResponse(Payload[PinnedChatMessageData]):
    pass


class PollsResponseChoices(TypedDict):
    id: str
    title: str
    votes: int
    channel_points_votes: int
    bits_votes: int


class PollsResponseData(TypedDict):
    id: str
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    title: str
    choices: list[PollsResponseChoices]
    bits_voting_enabled: bool
    bits_per_vote: int
    channel_points_voting_enabled: bool
    channel_points_per_vote: int
    status: Literal["ACTIVE", "COMPLETED", "TERMINATED", "ARCHIVED", "MODERATED", "INVALID"]
    duration: int
    started_at: str
    ended_at: str | None


class PollsResponse(Payload[PollsResponseData]):
    pagination: Pagination


class CreatePollResponse(Payload[PollsResponseData]):
    pass


class EndPollResponse(Payload[PollsResponseData]):
    pass


class PredictionsResponseTopPredictors(TypedDict):
    user_id: str
    user_name: str
    user_login: str
    channel_points_used: int
    channel_points_won: int


class PredictionsResponseOutcomes(TypedDict):
    id: str
    title: str
    users: int
    channel_points: int
    top_predictors: list[PredictionsResponseTopPredictors]
    color: Literal["BLUE", "PINK"]


class PredictionsResponseData(TypedDict):
    id: str
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    title: str
    winning_outcome_id: str | None
    outcomes: list[PredictionsResponseOutcomes]
    prediction_window: int
    status: Literal["ACTIVE", "CANCELED", "LOCKED", "RESOLVED"]
    created_at: str
    ended_at: str | None
    locked_at: str | None


class PredictionsResponse(Payload[PredictionsResponseData]):
    pagination: Pagination


class CreatePredictionResponse(Payload[PredictionsResponseData]):
    pass


class EndPredictionResponse(Payload[PredictionsResponseData]):
    pass


class StartARaidResponseData(TypedDict):
    created_at: str
    is_mature: bool


class StartARaidResponse(Payload[StartARaidResponseData]):
    pass


class ChannelStreamScheduleResponseCategory(TypedDict):
    id: str
    name: str


class ChannelStreamScheduleResponseSegments(TypedDict):
    id: str
    start_time: str
    end_time: str
    title: str
    canceled_until: str | None
    category: ChannelStreamScheduleResponseCategory | None
    is_recurring: bool


class ChannelStreamScheduleResponseVacation(TypedDict):
    start_time: str
    end_time: str


class ChannelStreamScheduleResponseData(TypedDict):
    segments: list[ChannelStreamScheduleResponseSegments]
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    vacation: ChannelStreamScheduleResponseVacation | None


class ChannelStreamScheduleResponse(TypedDict):
    data: ChannelStreamScheduleResponseData
    pagination: Pagination


class CreateChannelStreamScheduleSegmentResponse(TypedDict):
    data: ChannelStreamScheduleResponseData


class UpdateChannelStreamScheduleSegmentResponse(TypedDict):
    data: ChannelStreamScheduleResponseData


class SearchCategoriesResponseData(TypedDict):
    box_art_url: str
    name: str
    id: str


class SearchCategoriesResponse(Payload[SearchCategoriesResponseData]):
    pass


class SearchChannelsResponseData(TypedDict):
    broadcaster_language: str
    broadcaster_login: str
    display_name: str
    game_id: str
    game_name: str
    id: str
    is_live: bool
    tag_ids: list[str]
    tags: list[str]
    thumbnail_url: str
    title: str
    started_at: str


class SearchChannelsResponse(Payload[SearchChannelsResponseData]):
    pagination: Pagination


class StreamKeyResponseData(TypedDict):
    stream_key: str


class StreamKeyResponse(Payload[StreamKeyResponseData]):
    pass


class StreamsResponseData(TypedDict):
    id: str
    user_id: str
    user_login: str
    user_name: str
    # Game ID and name are empty when no category is set
    game_id: str
    game_name: str
    type: Literal["live", ""]
    title: str
    tags: list[str]
    viewer_count: int
    started_at: str
    language: str
    thumbnail_url: str
    tag_ids: list[str]
    is_mature: bool


class StreamsResponse(Payload[StreamsResponseData]):
    pagination: Pagination


class FollowedStreamsResponse(Payload[StreamsResponseData]):
    pagination: Pagination


class CreateStreamMarkerResponseData(TypedDict):
    id: str
    created_at: str
    position_seconds: int
    description: str


class CreateStreamMarkerResponse(Payload[CreateStreamMarkerResponseData]):
    pass


class StreamMarkersResponseMarkers(TypedDict):
    id: str
    created_at: str
    description: str
    position_seconds: int
    url: str


class StreamMarkersResponseVideos(TypedDict):
    video_id: str
    markers: list[StreamMarkersResponseMarkers]


class StreamMarkersResponseData(TypedDict):
    user_id: str
    user_name: str
    user_login: str
    videos: list[StreamMarkersResponseVideos]


class StreamMarkersResponse(Payload[StreamMarkersResponseData]):
    pagination: Pagination


class SuspiciousChatUserData(TypedDict):
    user_id: str
    broadcaster_id: str
    moderator_id: str
    updated_at: str
    status: Literal["ACTIVE_MONITORING", "RESTRICTED", "NO_TREATMENT"]
    types: list[Literal["MANUALLY_ADDED", "DETECTED_BAN_EVADER", "DETECTED_SUS_CHATTER", "BANNED_IN_SHARED_CHANNEL"]]


class SuspiciousChatUserResponse(Payload[SuspiciousChatUserData]):
    pass


class BroadcasterSubscriptionsResponseData(TypedDict):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    gifter_id: str
    gifter_login: str
    gifter_name: str
    is_gift: bool
    plan_name: str
    tier: Literal["1000", "2000", "3000"]
    user_id: str
    user_name: str
    user_login: str


class BroadcasterSubscriptionsResponse(Payload[BroadcasterSubscriptionsResponseData]):
    pagination: Pagination
    points: int
    total: int


class CheckUserSubscriptionResponseData(TypedDict):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    gifter_id: str | None
    gifter_login: str | None
    gifter_name: str | None
    is_gift: bool
    tier: Literal["1000", "2000", "3000"]


class CheckUserSubscriptionResponse(Payload[CheckUserSubscriptionResponseData]):
    pass


class ChannelTeamsResponseData(TypedDict):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    background_image_url: str
    banner: str
    created_at: str
    updated_at: str
    info: str
    thumbnail_url: str
    team_name: str
    team_display_name: str
    id: str


class ChannelTeamsResponse(Payload[ChannelTeamsResponseData]):
    pass


class TeamsResponseUsers(TypedDict):
    user_id: str
    user_login: str
    user_name: str


class TeamsResponseData(TypedDict):
    users: list[TeamsResponseUsers]
    background_image_url: str
    banner: str
    created_at: str
    updated_at: str
    info: str
    thumbnail_url: str
    team_name: str
    team_display_name: str
    id: str


class TeamsResponse(Payload[TeamsResponseData]):
    pass


class UsersResponseData(TypedDict):
    id: str
    login: str
    display_name: str
    type: Literal["admin", "global_mod", "staff", ""]
    broadcaster_type: Literal["affiliate", "partner", ""]
    description: str
    profile_image_url: str
    offline_image_url: str
    view_count: int
    email: str
    created_at: str


class UsersResponse(Payload[UsersResponseData]):
    pass


class UpdateUserResponse(Payload[UsersResponseData]):
    pass


class AuthorizationByUserResponseData(TypedDict):
    user_id: str
    user_name: str
    user_login: str
    scopes: list[str]
    has_authorized: bool


class AuthorizationByUserResponse(Payload[AuthorizationByUserResponseData]):
    pass


class UserBlockListResponseData(TypedDict):
    user_id: str
    user_login: str
    display_name: str


class UserBlockListResponse(Payload[UserBlockListResponseData]):
    pass


class UserExtensionsResponseData(TypedDict):
    id: str
    version: str
    name: str
    can_activate: bool
    type: list[Literal["component", "mobile", "overlay", "panel"]]


class UserExtensionsResponse(Payload[UserExtensionsResponseData]):
    pass


class UserPanelItem(TypedDict):
    active: bool
    id: str
    version: str
    name: str


class UserPanelOverlayItem(TypedDict):
    active: bool
    id: str
    version: str
    name: str


class UserPanelComponentItem(TypedDict):
    active: bool
    id: str
    version: str
    name: str
    x: int
    y: int


class UserActiveExtensionsResponseData(TypedDict):
    panel: dict[str, UserPanelItem]
    overlay: dict[str, UserPanelOverlayItem]
    component: dict[str, UserPanelComponentItem]


class UserActiveExtensionsResponse(TypedDict):
    data: UserActiveExtensionsResponseData


class UpdateUserExtensionsResponse(TypedDict):
    data: UserActiveExtensionsResponseData


class VideosResponseMutedSegments(TypedDict):
    duration: int
    offset: int


class VideosResponseData(TypedDict):
    id: str
    stream_id: str | None
    user_id: str
    user_login: str
    user_name: str
    title: str
    description: str
    created_at: str
    published_at: str
    url: str
    thumbnail_url: str
    viewable: str
    view_count: int
    language: str
    type: Literal["archive", "highlight", "upload"]
    duration: str
    muted_segments: list[VideosResponseMutedSegments] | None


class VideosResponse(Payload[VideosResponseData]):
    pagination: Pagination


class DeleteVideosResponse(Payload[str]):
    pass


class WarnChatUserResponseData(TypedDict):
    broadcaster_id: str
    user_id: str
    moderator_id: str
    reason: str


class WarnChatUserResponse(Payload[WarnChatUserResponseData]):
    pass
