# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["MoonbaseFile"]


class MoonbaseFile(BaseModel):
    id: str
    """Unique identifier for the object."""

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    download_url: str
    """A temporary, signed URL to download the file content.

    The URL expires after one hour.
    """

    filename: str
    """The original filename of the uploaded file."""

    name: str
    """The display name of the file."""

    size: float
    """The size of the file in bytes."""

    type: Literal["file"]
    """String representing the object’s type. Always `file` for this object."""

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""
