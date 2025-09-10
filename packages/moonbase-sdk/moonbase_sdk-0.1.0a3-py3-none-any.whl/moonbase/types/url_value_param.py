# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["URLValueParam"]


class URLValueParam(TypedDict, total=False):
    data: Required[str]
    """A valid URL, conforming to RFC 3986, up to 8,192 characters long.

    It should include the protocol, for example 'https://' or
    'mailto:support@moonbase.ai' etc.
    """

    type: Required[Literal["value/uri/url"]]
