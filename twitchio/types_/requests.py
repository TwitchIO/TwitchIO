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

from collections.abc import Sequence
from typing import Any, Literal, NotRequired, TypedDict

from .eventsub import ShardUpdateTransport


# ---- OAuth ----


class OAuthClientCredentialsRequestT(TypedDict):
    client_id: str
    client_secret: str
    grant_type: Literal["client_credentials"]


class OAuthRefreshRequestT(TypedDict, extra_items=Any):
    client_id: str
    client_secret: NotRequired[str]
    grant_type: Literal["refresh_token"]
    refresh_token: str


class OAuthRevokeRequestT(TypedDict):
    client_id: str
    token: str


class OAuthAuthFlowRequestT(TypedDict):
    client_id: str
    client_secret: str
    code: str
    grant_type: Literal["authorization_code"]
    redirect_uri: str


# ---- Conduits ----
class UpdateConduitsRequestT(TypedDict):
    id: str
    shard_count: int


class CreateConduitsRequestT(TypedDict):
    shard_count: int


class DeleteConduitsRequestT(TypedDict):
    id: str


class UpdateConduitsShardsRequestT(TypedDict):
    conduit_id: str
    shards: Sequence[ShardUpdateTransport]
