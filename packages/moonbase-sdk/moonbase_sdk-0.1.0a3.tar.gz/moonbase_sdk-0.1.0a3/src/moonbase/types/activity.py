# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from .._utils import PropertyInfo
from .activity_item_merged import ActivityItemMerged
from .activity_item_created import ActivityItemCreated
from .activity_meeting_held import ActivityMeetingHeld
from .activity_note_created import ActivityNoteCreated
from .activity_call_occurred import ActivityCallOccurred
from .activity_form_submitted import ActivityFormSubmitted
from .activity_item_mentioned import ActivityItemMentioned
from .activity_meeting_scheduled import ActivityMeetingScheduled
from .activity_inbox_message_sent import ActivityInboxMessageSent
from .activity_program_message_sent import ActivityProgramMessageSent
from .activity_program_message_failed import ActivityProgramMessageFailed
from .activity_program_message_opened import ActivityProgramMessageOpened
from .activity_program_message_bounced import ActivityProgramMessageBounced
from .activity_program_message_clicked import ActivityProgramMessageClicked
from .activity_program_message_shielded import ActivityProgramMessageShielded
from .activity_program_message_complained import ActivityProgramMessageComplained
from .activity_program_message_unsubscribed import ActivityProgramMessageUnsubscribed

__all__ = ["Activity"]

Activity: TypeAlias = Annotated[
    Union[
        ActivityCallOccurred,
        ActivityFormSubmitted,
        ActivityInboxMessageSent,
        ActivityItemCreated,
        ActivityItemMentioned,
        ActivityItemMerged,
        ActivityMeetingHeld,
        ActivityMeetingScheduled,
        ActivityNoteCreated,
        ActivityProgramMessageBounced,
        ActivityProgramMessageClicked,
        ActivityProgramMessageComplained,
        ActivityProgramMessageFailed,
        ActivityProgramMessageOpened,
        ActivityProgramMessageSent,
        ActivityProgramMessageShielded,
        ActivityProgramMessageUnsubscribed,
    ],
    PropertyInfo(discriminator="type"),
]
