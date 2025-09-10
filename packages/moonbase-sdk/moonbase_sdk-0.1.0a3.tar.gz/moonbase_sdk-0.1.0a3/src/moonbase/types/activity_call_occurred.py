# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .shared.pointer import Pointer

__all__ = ["ActivityCallOccurred"]


class ActivityCallOccurred(BaseModel):
    id: str
    """Unique identifier for the object."""

    call: Optional[Pointer] = None
    """A lightweight reference to another resource."""

    occurred_at: datetime
    """The time at which the event occurred, as an ISO 8601 timestamp in UTC."""

    type: Literal["activity/call_occurred"]
    """The type of activity. Always `activity/call_occurred`."""
