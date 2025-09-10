# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .field import Field
from .._models import BaseModel

__all__ = ["Collection"]


class Collection(BaseModel):
    id: str
    """Unique identifier for the object."""

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    fields: List[Field]
    """A list of `Field` objects that define the schema for items in this collection."""

    name: str
    """The user-facing name of the collection (e.g., “Organizations”)."""

    ref: str
    """A unique, stable, machine-readable identifier for the collection.

    This reference is used in API requests and does not change even if the `name` is
    updated.
    """

    type: Literal["collection"]
    """String representing the object’s type. Always `collection` for this object."""

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""

    description: Optional[str] = None
    """An optional, longer-form description of the collection's purpose."""

    views: Optional[List["View"]] = None
    """A list of saved `View` objects for presenting the collection's data.

    **Note:** Only present when requested using the `include` query parameter.
    """


from .view import View
