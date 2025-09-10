# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel
from .funnel_step import FunnelStep

__all__ = ["FunnelStepValue"]


class FunnelStepValue(BaseModel):
    data: FunnelStep
    """A specific funnel step, as configured on the Funnel"""

    type: Literal["value/funnel_step"]
