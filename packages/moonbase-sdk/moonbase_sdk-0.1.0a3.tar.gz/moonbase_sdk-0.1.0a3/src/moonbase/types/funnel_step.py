# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["FunnelStep"]


class FunnelStep(BaseModel):
    id: str
    """Unique identifier for the object."""

    name: str
    """The name of the step."""

    step_type: Literal["active", "success", "failure"]
    """The status of the step in the funnel flow.

    - `active`: represents an in progress state within the funnel
    - `success`: completed successfully and exited the funnel
    - `failure`: exited the funnel without conversion
    """

    type: Literal["funnel_step"]
    """String representing the object’s type. Always `funnel_step` for this object."""
