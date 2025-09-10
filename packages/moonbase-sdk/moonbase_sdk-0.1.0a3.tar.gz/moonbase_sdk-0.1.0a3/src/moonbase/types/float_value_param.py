# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["FloatValueParam"]


class FloatValueParam(TypedDict, total=False):
    data: Required[float]

    type: Required[Literal["value/number/unitless_float"]]
