# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel
from .shared.pointer import Pointer

__all__ = ["Address"]


class Address(BaseModel):
    id: str
    """Unique identifier for the object."""

    email: str
    """The email address."""

    role: Literal["from", "reply_to", "to", "cc", "bcc"]
    """The role of the address in the message.

    Can be `from`, `reply_to`, `to`, `cc`, or `bcc`.
    """

    type: Literal["message_address"]
    """String representing the object’s type.

    Always `message_address` for this object.
    """

    organization: Optional[Pointer] = None
    """A lightweight reference to another resource."""

    person: Optional[Pointer] = None
    """A lightweight reference to another resource."""
