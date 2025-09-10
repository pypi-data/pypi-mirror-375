# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["GeoValue"]


class GeoValue(BaseModel):
    data: str
    """A string that represents some geographic location.

    The exact format may vary based on context.
    """

    type: Literal["value/geo"]
