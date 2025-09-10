# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["SingleLineTextValueParam"]


class SingleLineTextValueParam(TypedDict, total=False):
    data: Required[str]
    """A single line of text, up to 1024 characters long.

    It should not contain line breaks.
    """

    type: Required[Literal["value/text/single_line"]]
