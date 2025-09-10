# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["Pointer"]


class Pointer(BaseModel):
    id: str
    """Unique identifier for the referenced object."""

    type: str
    """String indicating the type of the referenced object."""
