# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .._models import BaseModel
from .funnel_step import FunnelStep

__all__ = ["Funnel"]


class Funnel(BaseModel):
    id: str
    """Unique identifier for the object."""

    steps: List[FunnelStep]
    """An ordered list of `FunnelStep` objects that make up the funnel."""

    type: Literal["funnel"]
    """String representing the object’s type. Always `funnel` for this object."""
