# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .item_pointer import ItemPointer
from .shared.pointer import Pointer

__all__ = ["ActivityItemMentioned"]


class ActivityItemMentioned(BaseModel):
    id: str
    """Unique identifier for the object."""

    author: Optional[ItemPointer] = None
    """
    A reference to an `Item` within a specific `Collection`, providing the context
    needed to locate the item.
    """

    item: Optional[ItemPointer] = None
    """
    A reference to an `Item` within a specific `Collection`, providing the context
    needed to locate the item.
    """

    note: Optional[Pointer] = None
    """A lightweight reference to another resource."""

    occurred_at: datetime
    """The time at which the event occurred, as an ISO 8601 timestamp in UTC."""

    type: Literal["activity/item_mentioned"]
    """The type of activity. Always `activity/item_mentioned`."""
