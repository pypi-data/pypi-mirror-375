# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .funnel_step_param import FunnelStepParam
from .shared_params.pointer import Pointer

__all__ = ["FunnelStepValueParam", "Data"]

Data: TypeAlias = Union[FunnelStepParam, Pointer]


class FunnelStepValueParam(TypedDict, total=False):
    data: Required[Data]
    """A specific funnel step, as configured on the Funnel"""

    type: Required[Literal["value/funnel_step"]]
