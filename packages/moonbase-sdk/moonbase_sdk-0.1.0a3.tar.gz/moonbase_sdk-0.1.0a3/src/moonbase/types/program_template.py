# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .shared.formatted_text import FormattedText

__all__ = ["ProgramTemplate"]


class ProgramTemplate(BaseModel):
    id: str
    """Unique identifier for the object."""

    body: FormattedText
    """The body content of the email, which can include Liquid variables."""

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    subject: str
    """The subject line of the email, which can include Liquid variables."""

    type: Literal["program_template"]
    """String representing the object’s type.

    Always `program_template` for this object.
    """

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""

    program: Optional["Program"] = None
    """The `Program` that uses this template.

    **Note:** Only present when requested using the `include` query parameter.
    """


from .program import Program
