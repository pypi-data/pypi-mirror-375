# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["FloatValue"]


class FloatValue(BaseModel):
    data: float

    type: Literal["value/number/unitless_float"]
