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

from ..utils import MISSING
from .base import IdentifiableBaseModel


class PartialUser(IdentifiableBaseModel):
    __slots__ = ("display_name", "id", "login")
    __id_kind__ = "User"

    def __init__(self, id: str, login: str = MISSING, name: str = MISSING, display_name: str = MISSING) -> None:
        self.id = id
        self.login = login if login is not MISSING else name
        self.display_name = display_name

        if self.login is MISSING and self.display_name is not MISSING:
            self.login = self.display_name.lower()


class User(PartialUser):
    __slots__ = ()
    __id_kind__ = "User"
