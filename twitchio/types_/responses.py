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

from typing import Literal, TypedDict


class Payload[T](TypedDict):
    data: list[T]


# ---- OAUTH ----


class OAuthValidateResponseT(TypedDict):
    client_id: str
    login: str | None  # User | App
    scopes: list[str]
    user_id: str | None  # User | App
    expires_in: int


class OAuthRefreshResponseT(TypedDict):
    access_token: str
    expires_in: int
    refresh_token: str
    scope: list[str]
    token_type: Literal["bearer"]


class OAuthClientCredentialsResponseT(TypedDict):
    access_token: str
    expires_in: int
    token_type: Literal["bearer"]


class OAuthAuthFlowResponseT(TypedDict):
    access_token: str
    expires_in: int
    refresh_token: str
    scope: list[str]
    token_type: Literal["bearer"]


# ---- CONDUITS ----
class UpdateConduitsDataT(TypedDict):
    id: str
    shard_count: int


type UpdateConduitsResponseT = Payload[UpdateConduitsDataT]
