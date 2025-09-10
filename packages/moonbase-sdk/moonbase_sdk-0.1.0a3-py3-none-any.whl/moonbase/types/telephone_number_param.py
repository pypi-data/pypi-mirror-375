# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["TelephoneNumberParam"]


class TelephoneNumberParam(TypedDict, total=False):
    data: Required[str]
    """A telephone number in strictly formatted E.164 format.

    Do not include spaces, dashes, or parentheses etc.
    """

    type: Required[Literal["value/telephone_number"]]
