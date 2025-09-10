# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .address import Address
from .._models import BaseModel
from .shared.formatted_text import FormattedText

__all__ = ["EmailMessage", "Attachment"]


class Attachment(BaseModel):
    id: str
    """Unique identifier for the object."""

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    download_url: str
    """A temporary, signed URL to download the file content.

    The URL expires after one hour.
    """

    filename: str
    """The original name of the uploaded file, including its extension."""

    size: int
    """The size of the file in bytes."""

    type: Literal["message_attachment"]
    """String representing the object’s type.

    Always `message_attachment` for this object.
    """


class EmailMessage(BaseModel):
    id: str
    """Unique identifier for the object."""

    body: FormattedText
    """
    Structured content that can be rendered in multiple formats, currently
    supporting Markdown.
    """

    bulk: bool
    """`true` if the message appears to be part of a bulk mailing."""

    created_at: datetime
    """The time the message was received, as an ISO 8601 timestamp in UTC."""

    draft: bool
    """`true` if the message is a draft that has not been sent."""

    spam: bool
    """`true` if the message is classified as spam."""

    subject: str
    """The subject line of the email."""

    trash: bool
    """`true` if the message is in the trash."""

    type: Literal["email_message"]
    """String representing the object’s type. Always `email_message` for this object."""

    unread: bool
    """`true` if the message has not been read."""

    addresses: Optional[List[Address]] = None
    """A list of `Address` objects associated with the message (sender and recipients).

    **Note:** Only present when requested using the `include` query parameter.
    """

    attachments: Optional[List[Attachment]] = None
    """A list of `Attachment` objects on the message.

    **Note:** Only present when requested using the `include` query parameter.
    """

    conversation: Optional["InboxConversation"] = None
    """The `Conversation` thread this message is part of.

    **Note:** Only present when requested using the `include` query parameter.
    """

    summary: Optional[str] = None
    """A concise, system-generated summary of the email content."""


from .inbox_conversation import InboxConversation
