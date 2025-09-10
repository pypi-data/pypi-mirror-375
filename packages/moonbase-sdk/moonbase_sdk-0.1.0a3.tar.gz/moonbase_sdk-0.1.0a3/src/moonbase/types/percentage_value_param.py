# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["PercentageValueParam"]


class PercentageValueParam(TypedDict, total=False):
    data: Required[float]
    """
    A floating-point number representing a percentage value, for example 50.21 for
    50.21% or -1000 for -1000% etc.
    """

    type: Required[Literal["value/number/percentage"]]
