# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["View"]


class View(BaseModel):
    id: str
    """Unique identifier for the object."""

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    name: str
    """The name of the view."""

    type: Literal["view"]
    """String representing the object’s type. Always `view` for this object."""

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""

    view_type: Literal["table", "board"]
    """The type of view, such as `table` or `board`."""

    collection: Optional["Collection"] = None
    """The `Collection` this view belongs to.

    **Note:** Only present when requested using the `include` query parameter.
    """


from .collection import Collection
