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
import logging
import sys
from functools import cached_property
from typing import TYPE_CHECKING, Any, Self, TypeVar, Unpack, overload

import aiohttp

from twitchio import __version__

from ..exceptions import *
from ..models import *
from ..models.base import BaseModel
from ..utils import JSON_LOADS, MISSING
from .routes import RequestManager, Route


if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from twitchio.types_.eventsub import *
    from twitchio.types_.requests import *
    from twitchio.types_.responses import *


LOGGER: logging.Logger = logging.getLogger(__name__)
ModelT = TypeVar("ModelT", bound=BaseModel)


class HTTPClient:
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        self = super().__new__(cls)

        setattr(BaseModel, "_BaseModel__http", self)
        return self

    def __init__(
        self,
        *,
        session: aiohttp.ClientSession = MISSING,
        connector: aiohttp.TCPConnector = MISSING,
        client_id: str,
        client_secret: str | None,
        app_token: str = MISSING,
        is_dcf: bool = False,
        prefers_user: bool = False,
    ) -> None:
        self.__session = session
        self.__connector = connector
        self._user_session: bool = session is not MISSING
        self._client_id = client_id
        self._client_secret = client_secret
        self._app_token = app_token
        self._manager = RequestManager(self, is_dcf=is_dcf, prefers_user=prefers_user)
        self._has_setup: bool = False

        pyver = f"{sys.version_info[0]}.{sys.version_info[1]}"
        ua = "TwitchIOClient (https://github.com/TwitchIO/TwitchIO {0}) Python/{1} aiohttp/{2}"
        self.user_agent: str = ua.format(__version__, pyver, aiohttp.__version__)

    @cached_property
    def headers(self) -> dict[str, str]:
        return {"User-Agent": self.user_agent, "Client-ID": str(self._client_id)}

    async def setup(self) -> None:
        if self._has_setup:
            return

        if self.__session:
            session = self.__session
        else:
            conn = self.__connector if self.__connector is not MISSING else aiohttp.TCPConnector(ttl_dns_cache=300, limit=0)
            session = aiohttp.ClientSession(connector=conn)

        self.__session = session
        self._has_setup = True

        try:
            await self._manager.setup()
        except Exception as e:
            LOGGER.error(e, exc_info=e)
            await self.close()
        else:
            LOGGER.debug("Completed setup for %s.", type(self).__qualname__)

    def cleanup(self) -> None:
        if not self._user_session and self.__session.closed:
            self.__session = MISSING

        self._has_setup = False

    async def close(self) -> None:
        LOGGER.debug("Gracefully closing %s.", type(self).__name__)

        if not self._user_session:
            await self.__session.close()

        await self._manager.close()
        self.cleanup()

    @staticmethod
    async def json_or_text(resp: aiohttp.ClientResponse, /) -> dict[str, Any] | str:
        text = await resp.text(encoding="UTF-8")

        try:
            if "application/json" in resp.headers["content-type"]:
                return JSON_LOADS(text)
        except KeyError:
            pass

        return text

    async def request(self, route: Route) -> Any:
        failed: int | None = None
        container = self._manager.update_route(route, extras=self.headers) or self._manager._app_token
        limiter = container.bucket
        await limiter.acquire(route.cost)

        while True:
            method = route.method
            url = route.url

            LOGGER.debug("%s request: %r.", "Attempting" if not failed else "Re-attempting", route)

            try:
                async with self.__session.request(method, url, headers=route.headers, json=route.json or None) as resp:
                    limiter.update(resp.headers)
                    data = await self.json_or_text(resp)
                    status = resp.status

                    LOGGER.debug("Received response (%s) for %r: %s", status, route, data)

                    if status == 204:
                        return

                    if 200 <= status < 300:
                        return data

                    if failed:
                        if failed != status:
                            raise HTTPException(route=route, status=status) from HTTPException(route=route, status=failed)

                        raise HTTPException(route=route, status=status)

                    await self._manager.handle_error_code(route, resp=resp, status=status)
                    failed = status

            except OSError as e:
                # Peer reset errors
                if e.errno not in (54, 10054):
                    raise

                sleep = route.update_retries()
                if sleep is None:
                    raise

                await asyncio.sleep(sleep)

    async def request_json(self, route: Route) -> Any:
        route.headers.update({"Accept": "application/json"})
        return await self.request(route)

        # NOTE: Needed?
        # if isinstance(data, str):
        #     raise # TODO: ...

    async def request_paginated(self, route: Route) -> AsyncIterator[Any]:
        max_pages = route.max_pages or float("inf")
        max_results = route.max_results or float("inf")

        while True:
            resp = await self.request_json(route)
            yield resp

            max_pages -= 1
            if max_pages <= 0:
                return

            max_results -= len(resp.get("data", []))
            if max_results <= 0:
                return

            cursor = (resp.get("pagination") or {}).get("cursor")  # type: ignore
            if not cursor:
                return

            route.update_params({"after": cursor})

    @overload
    def build_model(self, model: type[ModelT], *, data: Any, key: None) -> ModelT: ...

    @overload
    def build_model(self, model: type[ModelT], *, data: Any, key: str = "data") -> list[ModelT]: ...

    def build_model(self, model: type[ModelT], *, data: Any, key: str | None = "data") -> ModelT | list[ModelT]:
        if key is None:
            return model(**data)

        inner = data.pop(key)
        return [model(**i, **data) for i in inner]

    # async def request_asset_head(self) -> ...: ...

    # async def request_asset(self) -> ...: ...

    # OAuth
    async def _oauth_validate(self, token: str) -> OAuthValidateResponseT:
        token = token.removeprefix("OAuth ").removeprefix("Bearer ")
        route = Route("GET", "oauth2/validate", use_id=True, headers={"Authorization": f"OAuth {token}"})

        return await self.request_json(route)

    async def oauth_validate(self, token: str) -> OAuthValidatePayload:
        resp = await self._oauth_validate(token)
        return self.build_model(OAuthValidatePayload, data=resp, key=None)

    async def _oauth_refresh(self, **kwargs: Unpack[OAuthRefreshRequestT]) -> OAuthRefreshResponseT:
        # NOTE: Can fail with 401; refresh_token is no longer valid
        # NOTE: 400 (Bad Request) is a custom payload response; invalid refresh_token
        # NOTE: client_secret is not required; public apps
        route = Route("POST", "oauth2/token", params=kwargs, use_id=True, encoded=True)
        return await self.request_json(route)

    async def oauth_refresh(self, **kwargs: Unpack[OAuthRefreshRequestT]) -> OAuthRefreshPayload:
        resp = await self._oauth_refresh(**kwargs)
        return self.build_model(OAuthRefreshPayload, data=resp, key=None)

    async def _oauth_fetch_user_token(self, **kwargs: Unpack[OAuthAuthFlowRequestT]) -> OAuthAuthFlowResponseT:
        route = Route("POST", "oauth2/token", params=kwargs, use_id=True, encoded=True)
        return await self.request_json(route)

    async def oauth_fetch_user_token(self, **kwargs: Unpack[OAuthAuthFlowRequestT]) -> OAuthAuthFlowPayload:
        resp = await self._oauth_fetch_user_token(**kwargs)
        return self.build_model(OAuthAuthFlowPayload, data=resp, key=None)

    async def _oauth_fetch_client_credentials(
        self, **kwargs: Unpack[OAuthClientCredentialsRequestT]
    ) -> OAuthClientCredentialsResponseT:
        route = Route("POST", "oauth2/token", params=kwargs, use_id=True, encoded=True)
        return await self.request_json(route)

    async def oauth_fetch_client_credentials(
        self, **kwargs: Unpack[OAuthClientCredentialsRequestT]
    ) -> OAuthClientCredentialsPayload:
        resp = await self._oauth_fetch_client_credentials(**kwargs)
        return self.build_model(OAuthClientCredentialsPayload, data=resp, key=None)

    async def oauth_revoke_token(self, **kwargs: Unpack[OAuthRevokeRequestT]) -> None:
        # NOTE: 400 Bad Request if the client ID is valid but the access token is not.
        # NOTE: 404 Not Found if the client ID is not valid.
        route = Route("POST", "oauth2/revoke", params=kwargs, use_id=True, encoded=True)
        return await self.request_json(route)

    async def _oauth_dcf(self) -> ...: ...

    async def _oauth_dcf_authorize(self) -> ...: ...

    def _get_auth_url(self) -> ...: ...

    # -- Ads --
    async def start_commercial(self) -> ...: ...
    async def get_ad_schedule(self) -> ...: ...
    async def snooze_next_ad(self) -> ...: ...

    # -- Analytics --
    async def get_extension_analytics(self) -> ...: ...
    async def get_game_analytics(self) -> ...: ...

    # -- Bits --
    async def get_bits_leaderboard(self) -> ...: ...
    async def get_cheermotes(self) -> ...: ...
    async def get_custom_powerup(self) -> ...: ...
    async def get_extension_transactions(self) -> ...: ...

    # -- Channels --
    async def get_channel_information(self) -> ...: ...
    async def modify_channel_information(self) -> ...: ...
    async def get_channel_editors(self) -> ...: ...
    async def get_followed_channels(self) -> ...: ...
    async def get_channel_followers(self) -> ...: ...

    # -- Channel Points --
    async def create_custom_rewards(self) -> ...: ...
    async def delete_custom_reward(self) -> ...: ...
    async def get_custom_reward(self) -> ...: ...
    async def get_custom_reward_redemption(self) -> ...: ...
    async def update_custom_reward(self) -> ...: ...
    async def update_redemption_status(self) -> ...: ...

    # -- Charity --
    async def get_charity_campaign(self) -> ...: ...
    async def get_charity_campaign_donations(self) -> ...: ...

    # -- Chat --
    async def get_chatters(self) -> ...: ...
    async def get_channel_emotes(self) -> ...: ...
    async def get_global_emotes(self) -> ...: ...
    async def get_emote_sets(self) -> ...: ...
    async def get_channel_chat_badges(self) -> ...: ...
    async def get_global_chat_badges(self) -> ...: ...
    async def get_chat_settings(self) -> ...: ...
    async def get_shared_chat_session(self) -> ...: ...
    async def get_user_emotes(self) -> ...: ...
    async def update_chat_settings(self) -> ...: ...
    async def send_chat_announcement(self) -> ...: ...
    async def send_a_shoutout(self) -> ...: ...
    async def send_chat_message(self) -> ...: ...
    async def get_pinned_chat_message(self) -> ...: ...
    async def pin_chat_message(self) -> ...: ...
    async def update_pinned_chat_message(self) -> ...: ...
    async def unpin_chat_message(self) -> ...: ...
    async def get_user_chat_color(self) -> ...: ...
    async def update_user_chat_color(self) -> ...: ...

    # -- Clips --
    async def create_clip(self) -> ...: ...
    async def create_clip_from_vod(self) -> ...: ...
    async def get_clips(self) -> ...: ...
    async def get_clips_download(self) -> ...: ...

    # -- Conduits --
    async def _get_conduits(self) -> GetConduitsResponseT:
        route = Route("GET", "eventsub/conduits")
        return await self.request_json(route)

    async def get_conduits(self) -> list[Conduit]:
        resp = await self._get_conduits()
        return self.build_model(Conduit, data=resp)

    async def _create_conduits(self, **kwargs: Unpack[CreateConduitsRequestT]) -> CreateConduitsResponseT:
        route = Route("POST", "eventsub/conduits", params=kwargs)
        return await self.request_json(route)

    async def create_conduits(self, **kwargs: Unpack[CreateConduitsRequestT]) -> list[Conduit]:
        resp = await self._create_conduits(**kwargs)
        return self.build_model(Conduit, data=resp)

    async def _update_conduits(self, **kwargs: Unpack[UpdateConduitsRequestT]) -> UpdateConduitsResponseT:
        route = Route("PATCH", "eventsub/conduits", json=kwargs)
        return await self.request_json(route)

    async def update_conduits(self, **kwargs: Unpack[UpdateConduitsRequestT]) -> list[Conduit]:
        resp: UpdateConduitsResponseT = await self._update_conduits(**kwargs)
        return self.build_model(Conduit, data=resp)

    async def delete_conduit(self, **kwargs: Unpack[DeleteConduitsRequestT]) -> None:
        # NOTE: 400 Bad Request	The id query parameter is required.
        # NOTE: 401 Unauthenticated	Authorization header required with an app access token.
        # NOTE: 404 Conduit not found; Conduit's owner must match the client ID in the access token.
        route = Route("DELETE", "eventsub/conduits", params=kwargs)
        return await self.request(route)

    async def get_conduit_shards(self, **kwargs: Unpack[GetConduitsShardsRequestT]) -> AsyncIterator[ShardData]:
        route = Route("GET", "eventsub/conduits/shards", params=kwargs)
        async for resp in self.request_paginated(route):
            yield resp

    async def _update_conduit_shards(self, **kwargs: Unpack[UpdateConduitsShardsRequestT]) -> UpdateConduitsShardsResponseT:
        params = {"conduit_id": kwargs.pop("conduit_id")}
        body = kwargs
        route = Route("PATCH", "eventsub/conduits/shards", could_404=True, params=params, json=body)

        return await self.request_json(route)

    async def update_conduit_shards(self, **kwargs: Unpack[UpdateConduitsShardsRequestT]) -> UpdatedShardPayload:
        resp: UpdateConduitsShardsResponseT = await self._update_conduit_shards(**kwargs)
        return UpdatedShardPayload(**resp)

    # -- CCLs --
    async def get_content_classification_labels(self) -> ...: ...

    # -- Entitlements --
    async def get_drops_entitlements(self) -> ...: ...
    async def update_drops_entitlements(self) -> ...: ...

    # -- Extensions --
    async def get_extension_configuration_segment(self) -> ...: ...
    async def set_extension_configuration_segment(self) -> ...: ...
    async def set_extension_required_configuration(self) -> ...: ...
    async def send_extension_pubsub_message(self) -> ...: ...
    async def get_extension_live_channels(self) -> ...: ...
    async def get_extension_secrets(self) -> ...: ...
    async def create_extension_secret(self) -> ...: ...
    async def send_extension_chat_message(self) -> ...: ...
    async def get_extensions(self) -> ...: ...
    async def get_released_extensions(self) -> ...: ...
    async def get_extension_bits_products(self) -> ...: ...
    async def update_extension_bits_product(self) -> ...: ...

    # -- EventSub --
    async def create_eventsub_subscription(self, **kwargs: Unpack[SubscriptionCreateRequest]) -> SubscriptionResponseT:
        route = Route("POST", "eventsub/subscriptions", json=kwargs)
        return await self.request_json(route)

    async def delete_eventsub_subscription(self) -> ...: ...

    async def _get_eventsub_subscriptions(
        self,
        **kwargs: Unpack[GetEventsubSubscriptionsRequestT],
    ) -> AsyncIterator[SubscriptionResponseT]:
        route = Route("GET", "eventsub/subscriptions", params=kwargs)
        async for resp in self.request_paginated(route):
            yield resp

    # -- Games --
    async def get_top_games(self) -> ...: ...
    async def get_games(self) -> ...: ...

    # -- Goals --
    async def get_creator_goals(self) -> ...: ...

    # -- Guest Star --
    async def get_channel_guest_star_settings(self) -> ...: ...
    async def update_channel_guest_star_settings(self) -> ...: ...
    async def get_guest_star_session(self) -> ...: ...
    async def create_guest_star_session(self) -> ...: ...
    async def end_guest_star_session(self) -> ...: ...
    async def get_guest_star_invites(self) -> ...: ...
    async def send_guest_star_invite(self) -> ...: ...
    async def delete_guest_star_invite(self) -> ...: ...
    async def assign_guest_star_slot(self) -> ...: ...
    async def update_guest_star_slot(self) -> ...: ...
    async def delete_guest_star_slot(self) -> ...: ...
    async def update_guest_star_slot_settings(self) -> ...: ...

    # -- Hype Train --
    async def get_hype_train_status(self) -> ...: ...

    # -- Moderation --
    async def check_automod_status(self) -> ...: ...
    async def manage_held_automod_messages(self) -> ...: ...
    async def get_automod_settings(self) -> ...: ...
    async def update_automod_settings(self) -> ...: ...
    async def get_banned_users(self) -> ...: ...
    async def ban_user(self) -> ...: ...
    async def unban_user(self) -> ...: ...
    async def get_unban_requests(self) -> ...: ...
    async def resolve_unban_requests(self) -> ...: ...
    async def get_blocked_terms(self) -> ...: ...
    async def add_blocked_term(self) -> ...: ...
    async def remove_blocked_term(self) -> ...: ...
    async def delete_chat_messages(self) -> ...: ...
    async def get_moderated_channels(self) -> ...: ...
    async def get_moderators(self) -> ...: ...
    async def add_channel_moderator(self) -> ...: ...
    async def remove_channel_moderator(self) -> ...: ...
    async def get_vips(self) -> ...: ...
    async def add_channel_vip(self) -> ...: ...
    async def remove_channel_vip(self) -> ...: ...
    async def update_shield_mode_status(self) -> ...: ...
    async def get_shield_mode_status(self) -> ...: ...
    async def warn_chat_user(self) -> ...: ...
    async def add_suspicious_status_to_chat_user(self) -> ...: ...
    async def remove_suspicious_status_from_chat_user(self) -> ...: ...

    # -- Polls --
    async def get_polls(self) -> ...: ...
    async def create_poll(self) -> ...: ...
    async def end_poll(self) -> ...: ...

    # -- Predictions --
    async def get_predictions(self) -> ...: ...
    async def create_prediction(self) -> ...: ...
    async def end_prediction(self) -> ...: ...

    # -- Raids --
    async def start_a_raid(self) -> ...: ...
    async def cancel_a_raid(self) -> ...: ...

    # -- Schedule --
    async def get_channel_stream_schedule(self) -> ...: ...
    async def get_channel_icalendar(self) -> ...: ...
    async def update_channel_stream_schedule(self) -> ...: ...
    async def create_channel_stream_schedule_segment(self) -> ...: ...
    async def update_channel_stream_schedule_segment(self) -> ...: ...
    async def delete_channel_stream_schedule_segment(self) -> ...: ...

    # -- Search --
    async def search_categories(self) -> ...: ...
    async def search_channels(self) -> ...: ...

    # -- Streams --
    async def get_stream_key(self) -> ...: ...
    async def get_streams(self) -> ...: ...
    async def get_followed_streams(self) -> ...: ...
    async def create_stream_marker(self) -> ...: ...
    async def get_stream_markers(self) -> ...: ...

    # -- Subscriptions --
    async def get_broadcaster_subscriptions(self) -> ...: ...
    async def check_user_subscription(self) -> ...: ...

    # -- Tags --
    async def get_all_stream_tags(self) -> ...: ...
    async def get_stream_tags(self) -> ...: ...

    # -- Teams --
    async def get_channel_teams(self) -> ...: ...
    async def get_teams(self) -> ...: ...

    # -- Users --
    async def get_users(self) -> ...: ...
    async def update_user(self) -> ...: ...
    async def get_authorization_by_user(self) -> ...: ...
    async def get_user_block_list(self) -> ...: ...
    async def block_user(self) -> ...: ...
    async def unblock_user(self) -> ...: ...
    async def get_user_extensions(self) -> ...: ...
    async def get_user_active_extensions(self) -> ...: ...
    async def update_user_extensions(self) -> ...: ...

    # -- Videos --
    async def get_videos(self) -> ...: ...
    async def delete_videos(self) -> ...: ...

    # -- Whispers --
    async def send_whisper(self) -> ...: ...
