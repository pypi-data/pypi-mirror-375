# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["URLValue"]


class URLValue(BaseModel):
    data: str
    """A valid URL, conforming to RFC 3986, up to 8,192 characters long.

    It should include the protocol, for example 'https://' or
    'mailto:support@moonbase.ai' etc.
    """

    type: Literal["value/uri/url"]
