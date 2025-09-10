# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["FunnelStepParam"]


class FunnelStepParam(TypedDict, total=False):
    id: Required[str]
    """Unique identifier for the object."""

    name: Required[str]
    """The name of the step."""

    step_type: Required[Literal["active", "success", "failure"]]
    """The status of the step in the funnel flow.

    - `active`: represents an in progress state within the funnel
    - `success`: completed successfully and exited the funnel
    - `failure`: exited the funnel without conversion
    """

    type: Required[Literal["funnel_step"]]
    """String representing the object’s type. Always `funnel_step` for this object."""
