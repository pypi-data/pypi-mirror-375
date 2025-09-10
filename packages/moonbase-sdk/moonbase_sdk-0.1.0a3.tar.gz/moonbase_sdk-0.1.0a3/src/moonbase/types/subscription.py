# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Subscription"]


class Subscription(BaseModel):
    event_type: Literal[
        "activity/call_occurred",
        "activity/form_submitted",
        "activity/inbox_message_sent",
        "activity/item_created",
        "activity/item_mentioned",
        "activity/item_merged",
        "activity/meeting_held",
        "activity/meeting_scheduled",
        "activity/note_created",
        "activity/program_message_bounced",
        "activity/program_message_clicked",
        "activity/program_message_complained",
        "activity/program_message_failed",
        "activity/program_message_opened",
        "activity/program_message_sent",
        "activity/program_message_shielded",
        "activity/program_message_unsubscribed",
    ]
    """
    The type of event that will trigger notifications to the endpoint (e.g.,
    `activity/item_created`).
    """

    type: Literal["webhook_subscription"]
    """String representing the object’s type.

    Always `webhook_subscription` for this object.
    """
