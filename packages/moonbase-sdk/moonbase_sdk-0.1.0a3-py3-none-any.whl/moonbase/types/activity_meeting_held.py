# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .shared.pointer import Pointer

__all__ = ["ActivityMeetingHeld"]


class ActivityMeetingHeld(BaseModel):
    id: str
    """Unique identifier for the object."""

    meeting: Optional[Pointer] = None
    """A lightweight reference to another resource."""

    occurred_at: datetime
    """The time at which the event occurred, as an ISO 8601 timestamp in UTC."""

    type: Literal["activity/meeting_held"]
    """The type of activity. Always `activity/meeting_held`."""
