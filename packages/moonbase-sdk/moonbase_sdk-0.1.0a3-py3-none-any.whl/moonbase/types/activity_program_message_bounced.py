# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .item_pointer import ItemPointer
from .shared.pointer import Pointer

__all__ = ["ActivityProgramMessageBounced"]


class ActivityProgramMessageBounced(BaseModel):
    id: str
    """Unique identifier for the object."""

    occurred_at: datetime
    """The time at which the event occurred, as an ISO 8601 timestamp in UTC."""

    program_message: Optional[Pointer] = None
    """A lightweight reference to another resource."""

    recipient: Optional[ItemPointer] = None
    """
    A reference to an `Item` within a specific `Collection`, providing the context
    needed to locate the item.
    """

    type: Literal["activity/program_message_bounced"]
    """The type of activity. Always `activity/program_message_bounced`."""

    bounce_type: Optional[str] = None
    """
    The type of bounce (e.g., `Permanent` for hard bounces, `Temporary` for soft
    bounces).
    """

    bounced_recipient_emails: Optional[List[str]] = None
    """List of email addresses that bounced."""
