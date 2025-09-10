# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Program", "ActivityMetrics"]


class ActivityMetrics(BaseModel):
    bounced: int
    """The number of emails that could not be delivered."""

    clicked: int
    """The number of recipients who clicked at least one link."""

    complained: int
    """The number of recipients who marked the email as spam."""

    failed: int
    """The number of emails that failed to send due to a technical issue."""

    opened: int
    """The number of recipients who opened the email."""

    sent: int
    """The total number of emails successfully sent."""

    shielded: int
    """The number of emails blocked by delivery protection rules."""

    unsubscribed: int
    """The number of recipients who unsubscribed."""


class Program(BaseModel):
    id: str
    """Unique identifier for the object."""

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    status: Literal["draft", "published", "paused", "archived"]
    """The current status of the program.

    Can be `draft`, `published`, `paused`, or `archived`.
    """

    track_clicks: bool
    """`true` if link clicks are tracked for this program."""

    track_opens: bool
    """`true` if email opens are tracked for this program."""

    trigger: Literal["api", "broadcast"]
    """The sending trigger for the program.

    Can be `api` for transactional sends or `broadcast` for scheduled sends.
    """

    type: Literal["program"]
    """String representing the object’s type. Always `program` for this object."""

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""

    activity_metrics: Optional[ActivityMetrics] = None
    """A `ProgramActivityMetrics` object summarizing engagement for this program.

    **Note:** Only present when requested using the `include` query parameter.
    """

    display_name: Optional[str] = None
    """The user-facing name of the program."""

    program_template: Optional["ProgramTemplate"] = None
    """The `ProgramTemplate` used for messages in this program.

    **Note:** Only present when requested using the `include` query parameter.
    """

    scheduled_at: Optional[datetime] = None
    """
    For `broadcast` programs, the time the program is scheduled to send, as an ISO
    8601 timestamp in UTC.
    """


from .program_template import ProgramTemplate
