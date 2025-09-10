# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["WebhookEndpointCreateParams", "Subscription"]


class WebhookEndpointCreateParams(TypedDict, total=False):
    status: Required[Literal["disabled", "enabled"]]
    """Indicates whether the endpoint is enabled."""

    url: Required[str]
    """The HTTPS URL where webhook events will be sent."""

    subscriptions: Iterable[Subscription]
    """An array of event types that this endpoint should receive notifications for."""


class Subscription(TypedDict, total=False):
    event_type: Required[
        Literal[
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
    ]
    """
    The type of event that will trigger notifications to the endpoint (e.g.,
    `activity/item_created`).
    """
