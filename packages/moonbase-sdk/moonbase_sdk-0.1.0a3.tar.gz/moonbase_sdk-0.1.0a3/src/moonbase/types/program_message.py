# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ProgramMessage"]


class ProgramMessage(BaseModel):
    id: str
    """Unique identifier for the object."""

    created_at: datetime
    """
    Time at which the message was created and enqueued for sending, as an ISO 8601
    timestamp in UTC.
    """

    program_template: "ProgramTemplate"
    """The `ProgramTemplate` used to generate this message."""

    type: Literal["program_message"]
    """String representing the object’s type.

    Always `program_message` for this object.
    """

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""


from .program_template import ProgramTemplate
