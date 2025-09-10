# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .item_pointer import ItemPointer
from .shared.pointer import Pointer

__all__ = ["ActivityProgramMessageSent"]


class ActivityProgramMessageSent(BaseModel):
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

    type: Literal["activity/program_message_sent"]
    """The type of activity. Always `activity/program_message_sent`."""

    recipient_emails: Optional[List[str]] = None
    """List of email addresses the message was sent to."""
