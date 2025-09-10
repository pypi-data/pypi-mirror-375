# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["BooleanValueParam"]


class BooleanValueParam(TypedDict, total=False):
    data: Required[bool]

    type: Required[Literal["value/boolean"]]
