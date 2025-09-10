# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .inbox import Inbox
from .._models import BaseModel

__all__ = ["InboxConversation", "Tag"]


class Tag(BaseModel):
    id: str
    """Unique identifier for the object."""

    name: str
    """The name of the tag."""

    type: Literal["tag"]
    """String representing the object’s type. Always `tag` for this object."""


class InboxConversation(BaseModel):
    id: str
    """Unique identifier for the object."""

    bulk: bool
    """`true` if the conversation appears to be part of a bulk mailing."""

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    draft: bool
    """`true` if a new draft reply to this conversation has been started."""

    follow_up: bool
    """Whether the conversation is marked for follow-up."""

    last_message_at: datetime
    """
    The time of the most recent activity in the conversation, as an ISO 8601
    timestamp in UTC.
    """

    spam: bool
    """`true` if the conversation is marked as spam."""

    state: Literal["unassigned", "active", "closed", "waiting"]
    """The current state, which can be `unassigned`, `active`, `closed`, or `waiting`."""

    subject: str
    """The subject line of the conversation."""

    tags: List[Tag]
    """A list of `Tag` objects applied to this conversation."""

    trash: bool
    """`true` if the conversation is in the trash."""

    type: Literal["inbox_conversation"]
    """String representing the object’s type.

    Always `inbox_conversation` for this object.
    """

    unread: bool
    """`true` if the conversation contains unread messages."""

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""

    inbox: Optional[Inbox] = None
    """The `Inbox` that this conversations belongs to.

    **Note:** Only present when requested using the `include` query parameter.
    """

    messages: Optional[List["EmailMessage"]] = None
    """The `EmailMessage` objects that belong to this conversation.

    **Note:** Only present when requested using the `include` query parameter.
    """

    unsnooze_at: Optional[datetime] = None
    """
    If the conversation is snoozed, this is the time it will reappear in the inbox,
    as an ISO 8601 timestamp in UTC.
    """


from .email_message import EmailMessage
