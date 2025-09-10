# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["PercentageValue"]


class PercentageValue(BaseModel):
    data: float
    """
    A floating-point number representing a percentage value, for example 50.21 for
    50.21% or -1000 for -1000% etc.
    """

    type: Literal["value/number/percentage"]
