# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["MultiLineTextValueParam"]


class MultiLineTextValueParam(TypedDict, total=False):
    data: Required[str]
    """Text which may contain line breaks, can be up to 65,536 characters long.

    Do not use markdown formatting, just plain text.
    """

    type: Required[Literal["value/text/multi_line"]]
