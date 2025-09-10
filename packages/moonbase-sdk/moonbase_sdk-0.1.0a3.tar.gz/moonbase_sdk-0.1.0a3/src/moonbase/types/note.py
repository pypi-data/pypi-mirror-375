# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .shared.formatted_text import FormattedText

__all__ = ["Note"]


class Note(BaseModel):
    id: str
    """Unique identifier for the object."""

    body: FormattedText
    """The main content of the note."""

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    type: Literal["note"]
    """String representing the object’s type. Always `note` for this object."""

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""

    summary: Optional[str] = None
    """A short, system-generated summary of the note's content."""

    title: Optional[str] = None
    """An optional title for the note."""
