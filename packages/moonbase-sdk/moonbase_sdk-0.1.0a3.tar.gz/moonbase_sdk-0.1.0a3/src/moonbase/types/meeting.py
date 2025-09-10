# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .attendee import Attendee
from .organizer import Organizer

__all__ = ["Meeting"]


class Meeting(BaseModel):
    id: str
    """Unique identifier for the object."""

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    end_at: datetime
    """The end time of the meeting, as an ISO 8601 timestamp in UTC."""

    i_cal_uid: str
    """The globally unique iCalendar UID for the meeting event."""

    provider_id: str
    """
    The unique identifier for the meeting from the external calendar provider (e.g.,
    Google Calendar).
    """

    start_at: datetime
    """The start time of the meeting, as an ISO 8601 timestamp in UTC."""

    time_zone: str
    """
    The IANA time zone in which the meeting is scheduled (e.g.,
    `America/Los_Angeles`).
    """

    type: Literal["meeting"]
    """String representing the object’s type. Always `meeting` for this object."""

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""

    attendees: Optional[List[Attendee]] = None
    """A list of `Attendee` objects for the meeting.

    **Note:** Only present when requested using the `include` query parameter.
    """

    description: Optional[str] = None
    """A detailed description or agenda for the meeting."""

    duration: Optional[float] = None
    """The duration of the meeting in seconds."""

    location: Optional[str] = None
    """The physical or virtual location of the meeting."""

    organizer: Optional[Organizer] = None
    """The `Organizer` of the meeting.

    **Note:** Only present when requested using the `include` query parameter.
    """

    provider_uri: Optional[str] = None
    """A URL to access the meeting in the external provider's system."""

    recording_url: Optional[str] = None
    """A temporary, signed URL to download the meeting recording.

    The URL expires after one hour.
    """

    summary_ante: Optional[str] = None
    """A summary or notes generated before the meeting."""

    summary_post: Optional[str] = None
    """A summary or notes generated after the meeting."""

    title: Optional[str] = None
    """The title or subject of the meeting."""

    transcript_url: Optional[str] = None
    """A temporary, signed URL to download the meeting transcript.

    The URL expires after one hour.
    """
