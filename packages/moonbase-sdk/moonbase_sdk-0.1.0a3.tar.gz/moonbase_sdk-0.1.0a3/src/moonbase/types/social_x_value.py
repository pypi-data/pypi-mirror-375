# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["SocialXValue", "Data"]


class Data(BaseModel):
    url: str
    """The full URL to the X profile, starting with 'https://x.com/'"""

    username: str
    """
    The X username, up to 15 characters long, containing only lowercase letters
    (a-z), uppercase letters (A-Z), numbers (0-9), and underscores (\\__). Does not
    include the '@' symbol prefix.
    """


class SocialXValue(BaseModel):
    data: Data
    """
    Social media profile information including both the full URL and extracted
    username.
    """

    type: Literal["value/uri/social_x"]
