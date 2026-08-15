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

from typing import Unpack

from ..types_.responses import OAuthRefreshResponseT, OAuthValidateResponseT
from .base import BaseModel


__all__ = ("OAuthRefreshPayload", "OAuthValidatePayload")


class OAuthValidatePayload(BaseModel):
    __slots__ = ("client_id", "expires_in", "login", "scopes", "user_id")

    def __init__(self, **data: Unpack[OAuthValidateResponseT]) -> None:
        self.client_id = data["client_id"]
        self.login = data["login"]
        self.scopes = data["scopes"]  # TODO: Scopes object...
        self.user_id = data["user_id"]
        self.expires_in = data["expires_in"]  # TODO: datetime?/delta?


class OAuthRefreshPayload(BaseModel):
    __slots__ = ("access_token", "expires_in", "refresh_token", "scopes", "token_type")

    def __init__(self, **data: Unpack[OAuthRefreshResponseT]) -> None:
        self.access_token = data["access_token"]
        self.expires_in = data["expires_in"]
        self.refresh_token = data["refresh_token"]
        self.scopes = data["scope"]  # TODO: Scopes object...
        self.token_type = data["token_type"]
