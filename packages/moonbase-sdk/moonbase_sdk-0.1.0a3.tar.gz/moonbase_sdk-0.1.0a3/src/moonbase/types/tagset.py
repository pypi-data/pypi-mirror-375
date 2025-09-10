# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Tagset", "Tag"]


class Tag(BaseModel):
    id: str
    """Unique identifier for the object."""

    name: str
    """The name of the tag."""

    type: Literal["tag"]
    """String representing the object’s type. Always `tag` for this object."""


class Tagset(BaseModel):
    id: str
    """Unique identifier for the object."""

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    name: str
    """The name of the tagset."""

    tags: List[Tag]
    """A list of `Tag` objects belonging to this tagset."""

    type: Literal["tagset"]
    """String representing the object’s type. Always `tagset` for this object."""

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""

    description: Optional[str] = None
    """An optional description of the tagset's purpose."""
