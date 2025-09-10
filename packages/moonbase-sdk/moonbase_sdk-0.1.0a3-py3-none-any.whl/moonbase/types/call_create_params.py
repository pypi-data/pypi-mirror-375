# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["CallCreateParams", "Participant", "Recording", "Transcript", "TranscriptCue"]


class CallCreateParams(TypedDict, total=False):
    direction: Required[Literal["incoming", "outgoing"]]
    """The direction of the call, either `incoming` or `outgoing`."""

    participants: Required[Iterable[Participant]]
    """An array of participants involved in the call."""

    provider: Required[str]
    """The name of the phone provider that handled the call (e.g., `openphone`)."""

    provider_id: Required[str]
    """The unique identifier for the call from the provider's system."""

    provider_status: Required[str]
    """The status of the call."""

    start_at: Required[Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]]
    """The time the call started, as an ISO 8601 timestamp in UTC."""

    answered_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """The time the call was answered, as an ISO 8601 timestamp in UTC."""

    end_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """The time the call ended, as an ISO 8601 timestamp in UTC."""

    provider_metadata: Dict[str, object]
    """A hash of additional metadata from the provider."""

    recordings: Iterable[Recording]
    """Any recordings associated with the call."""

    transcript: Transcript
    """A transcript of the call."""


class Participant(TypedDict, total=False):
    phone: Required[str]
    """The E.164 formatted phone number of the participant."""

    role: Required[Literal["caller", "callee", "other"]]
    """The role of the participant in the call. Can be `caller`, `callee`, or `other`."""


class Recording(TypedDict, total=False):
    content_type: Required[str]
    """The content type of the recording.

    Note that only `audio/mpeg` is supported at this time.
    """

    provider_id: Required[str]
    """The unique identifier for the recording from the provider's system."""

    url: Required[str]
    """The URL pointing to the recording."""


_TranscriptCueReservedKeywords = TypedDict(
    "_TranscriptCueReservedKeywords",
    {
        "from": float,
    },
    total=False,
)


class TranscriptCue(_TranscriptCueReservedKeywords, total=False):
    speaker: Required[str]
    """The E.164 formatted phone number of the speaker."""

    text: Required[str]
    """The text spoken during the slice."""

    to: Required[float]
    """The end time of the slice, in fractional seconds from the start of the call."""


class Transcript(TypedDict, total=False):
    cues: Required[Iterable[TranscriptCue]]
    """
    A list of cues that identify the text spoken in specific time slices of the
    call.
    """
