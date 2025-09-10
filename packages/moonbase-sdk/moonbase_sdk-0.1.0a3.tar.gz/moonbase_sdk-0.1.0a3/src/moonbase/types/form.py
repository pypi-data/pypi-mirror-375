# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Form"]


class Form(BaseModel):
    id: str
    """Unique identifier for the object."""

    collection: "Collection"
    """The `Collection` that submissions to this form are saved to."""

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    name: str
    """The name of the form, used as the title on its public page."""

    pages_enabled: bool
    """`true` if the form is available at a public URL."""

    type: Literal["form"]
    """String representing the object’s type. Always `form` for this object."""

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""

    pages_url: Optional[str] = None
    """The public URL for the form, if `pages_enabled` is `true`."""

    redirect_url: Optional[str] = None
    """An optional URL to redirect users to after a successful submission."""


from .collection import Collection
