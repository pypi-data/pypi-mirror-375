# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .item_pointer import ItemPointer

__all__ = ["ActivityItemCreated"]


class ActivityItemCreated(BaseModel):
    id: str
    """Unique identifier for the object."""

    item: Optional[ItemPointer] = None
    """
    A reference to an `Item` within a specific `Collection`, providing the context
    needed to locate the item.
    """

    occurred_at: datetime
    """The time at which the event occurred, as an ISO 8601 timestamp in UTC."""

    type: Literal["activity/item_created"]
    """The type of activity. Always `activity/item_created`."""
