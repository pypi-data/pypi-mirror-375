# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .tagset import Tagset
from .._models import BaseModel

__all__ = ["Inbox"]


class Inbox(BaseModel):
    id: str
    """Unique identifier for the object."""

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    name: str
    """The display name of the inbox."""

    type: Literal["inbox"]
    """String representing the object’s type. Always `inbox` for this object."""

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""

    tagset: Optional[Tagset] = None
    """
    The `Tagset` associated with this inbox, which defines the tags available for
    its conversations.

    **Note:** Only present when requested using the `include` query parameter.
    """
