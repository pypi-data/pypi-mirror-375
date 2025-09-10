# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel
from .shared.pointer import Pointer

__all__ = ["Organizer"]


class Organizer(BaseModel):
    id: str
    """Unique identifier for the object."""

    email: str
    """The email address of the organizer."""

    type: Literal["meeting_organizer"]
    """String representing the object’s type.

    Always `meeting_organizer` for this object.
    """

    organization: Optional[Pointer] = None
    """A lightweight reference to another resource."""

    person: Optional[Pointer] = None
    """A lightweight reference to another resource."""
