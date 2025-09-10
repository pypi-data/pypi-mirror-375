# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from . import form, view, program, collection, email_message, program_message, program_template, inbox_conversation
from .. import _compat
from .call import Call as Call
from .form import Form as Form
from .item import Item as Item
from .note import Note as Note
from .view import View as View
from .field import Field as Field
from .inbox import Inbox as Inbox
from .value import Value as Value
from .funnel import Funnel as Funnel
from .shared import Error as Error, Pointer as Pointer, FormattedText as FormattedText
from .tagset import Tagset as Tagset
from .address import Address as Address
from .meeting import Meeting as Meeting
from .program import Program as Program
from .activity import Activity as Activity
from .attendee import Attendee as Attendee
from .endpoint import Endpoint as Endpoint
from .geo_field import GeoField as GeoField
from .geo_value import GeoValue as GeoValue
from .organizer import Organizer as Organizer
from .url_field import URLField as URLField
from .url_value import URLValue as URLValue
from .collection import Collection as Collection
from .date_field import DateField as DateField
from .date_value import DateValue as DateValue
from .email_field import EmailField as EmailField
from .email_value import EmailValue as EmailValue
from .field_value import FieldValue as FieldValue
from .float_field import FloatField as FloatField
from .float_value import FloatValue as FloatValue
from .funnel_step import FunnelStep as FunnelStep
from .stage_field import StageField as StageField
from .value_param import ValueParam as ValueParam
from .choice_field import ChoiceField as ChoiceField
from .choice_value import ChoiceValue as ChoiceValue
from .domain_field import DomainField as DomainField
from .domain_value import DomainValue as DomainValue
from .item_pointer import ItemPointer as ItemPointer
from .subscription import Subscription as Subscription
from .boolean_field import BooleanField as BooleanField
from .boolean_value import BooleanValue as BooleanValue
from .email_message import EmailMessage as EmailMessage
from .integer_field import IntegerField as IntegerField
from .integer_value import IntegerValue as IntegerValue
from .moonbase_file import MoonbaseFile as MoonbaseFile
from .datetime_field import DatetimeField as DatetimeField
from .datetime_value import DatetimeValue as DatetimeValue
from .monetary_field import MonetaryField as MonetaryField
from .monetary_value import MonetaryValue as MonetaryValue
from .relation_field import RelationField as RelationField
from .relation_value import RelationValue as RelationValue
from .social_x_field import SocialXField as SocialXField
from .social_x_value import SocialXValue as SocialXValue
from .geo_value_param import GeoValueParam as GeoValueParam
from .program_message import ProgramMessage as ProgramMessage
from .url_value_param import URLValueParam as URLValueParam
from .date_value_param import DateValueParam as DateValueParam
from .file_list_params import FileListParams as FileListParams
from .form_list_params import FormListParams as FormListParams
from .note_list_params import NoteListParams as NoteListParams
from .percentage_field import PercentageField as PercentageField
from .percentage_value import PercentageValue as PercentageValue
from .program_template import ProgramTemplate as ProgramTemplate
from .telephone_number import TelephoneNumber as TelephoneNumber
from .email_value_param import EmailValueParam as EmailValueParam
from .field_value_param import FieldValueParam as FieldValueParam
from .float_value_param import FloatValueParam as FloatValueParam
from .funnel_step_param import FunnelStepParam as FunnelStepParam
from .funnel_step_value import FunnelStepValue as FunnelStepValue
from .inbox_list_params import InboxListParams as InboxListParams
from .call_create_params import CallCreateParams as CallCreateParams
from .call_upsert_params import CallUpsertParams as CallUpsertParams
from .choice_value_param import ChoiceValueParam as ChoiceValueParam
from .collection_pointer import CollectionPointer as CollectionPointer
from .domain_value_param import DomainValueParam as DomainValueParam
from .inbox_conversation import InboxConversation as InboxConversation
from .item_pointer_param import ItemPointerParam as ItemPointerParam
from .tagset_list_params import TagsetListParams as TagsetListParams
from .boolean_value_param import BooleanValueParam as BooleanValueParam
from .choice_field_option import ChoiceFieldOption as ChoiceFieldOption
from .integer_value_param import IntegerValueParam as IntegerValueParam
from .meeting_list_params import MeetingListParams as MeetingListParams
from .program_list_params import ProgramListParams as ProgramListParams
from .activity_item_merged import ActivityItemMerged as ActivityItemMerged
from .activity_list_params import ActivityListParams as ActivityListParams
from .datetime_value_param import DatetimeValueParam as DatetimeValueParam
from .monetary_value_param import MonetaryValueParam as MonetaryValueParam
from .relation_value_param import RelationValueParam as RelationValueParam
from .view_retrieve_params import ViewRetrieveParams as ViewRetrieveParams
from .activity_item_created import ActivityItemCreated as ActivityItemCreated
from .activity_meeting_held import ActivityMeetingHeld as ActivityMeetingHeld
from .activity_note_created import ActivityNoteCreated as ActivityNoteCreated
from .inbox_retrieve_params import InboxRetrieveParams as InboxRetrieveParams
from .multi_line_text_field import MultiLineTextField as MultiLineTextField
from .multi_line_text_value import MultiLineTextValue as MultiLineTextValue
from .activity_call_occurred import ActivityCallOccurred as ActivityCallOccurred
from .collection_list_params import CollectionListParams as CollectionListParams
from .percentage_value_param import PercentageValueParam as PercentageValueParam
from .single_line_text_field import SingleLineTextField as SingleLineTextField
from .single_line_text_value import SingleLineTextValue as SingleLineTextValue
from .social_linked_in_field import SocialLinkedInField as SocialLinkedInField
from .social_linked_in_value import SocialLinkedInValue as SocialLinkedInValue
from .telephone_number_field import TelephoneNumberField as TelephoneNumberField
from .telephone_number_param import TelephoneNumberParam as TelephoneNumberParam
from .activity_form_submitted import ActivityFormSubmitted as ActivityFormSubmitted
from .activity_item_mentioned import ActivityItemMentioned as ActivityItemMentioned
from .funnel_step_value_param import FunnelStepValueParam as FunnelStepValueParam
from .meeting_retrieve_params import MeetingRetrieveParams as MeetingRetrieveParams
from .program_retrieve_params import ProgramRetrieveParams as ProgramRetrieveParams
from .collection_pointer_param import CollectionPointerParam as CollectionPointerParam
from .choice_field_option_param import ChoiceFieldOptionParam as ChoiceFieldOptionParam
from .inbox_message_list_params import InboxMessageListParams as InboxMessageListParams
from .activity_meeting_scheduled import ActivityMeetingScheduled as ActivityMeetingScheduled
from .collection_retrieve_params import CollectionRetrieveParams as CollectionRetrieveParams
from .activity_inbox_message_sent import ActivityInboxMessageSent as ActivityInboxMessageSent
from .multi_line_text_value_param import MultiLineTextValueParam as MultiLineTextValueParam
from .program_message_send_params import ProgramMessageSendParams as ProgramMessageSendParams
from .program_template_list_params import ProgramTemplateListParams as ProgramTemplateListParams
from .single_line_text_value_param import SingleLineTextValueParam as SingleLineTextValueParam
from .webhook_endpoint_list_params import WebhookEndpointListParams as WebhookEndpointListParams
from .activity_program_message_sent import ActivityProgramMessageSent as ActivityProgramMessageSent
from .inbox_message_retrieve_params import InboxMessageRetrieveParams as InboxMessageRetrieveParams
from .inbox_conversation_list_params import InboxConversationListParams as InboxConversationListParams
from .webhook_endpoint_create_params import WebhookEndpointCreateParams as WebhookEndpointCreateParams
from .webhook_endpoint_update_params import WebhookEndpointUpdateParams as WebhookEndpointUpdateParams
from .activity_program_message_failed import ActivityProgramMessageFailed as ActivityProgramMessageFailed
from .activity_program_message_opened import ActivityProgramMessageOpened as ActivityProgramMessageOpened
from .activity_program_message_bounced import ActivityProgramMessageBounced as ActivityProgramMessageBounced
from .activity_program_message_clicked import ActivityProgramMessageClicked as ActivityProgramMessageClicked
from .program_template_retrieve_params import ProgramTemplateRetrieveParams as ProgramTemplateRetrieveParams
from .activity_program_message_shielded import ActivityProgramMessageShielded as ActivityProgramMessageShielded
from .inbox_conversation_retrieve_params import InboxConversationRetrieveParams as InboxConversationRetrieveParams
from .activity_program_message_complained import ActivityProgramMessageComplained as ActivityProgramMessageComplained
from .activity_program_message_unsubscribed import (
    ActivityProgramMessageUnsubscribed as ActivityProgramMessageUnsubscribed,
)

# Rebuild cyclical models only after all modules are imported.
# This ensures that, when building the deferred (due to cyclical references) model schema,
# Pydantic can resolve the necessary references.
# See: https://github.com/pydantic/pydantic/issues/11250 for more context.
if _compat.PYDANTIC_V1:
    collection.Collection.update_forward_refs()  # type: ignore
    view.View.update_forward_refs()  # type: ignore
    inbox_conversation.InboxConversation.update_forward_refs()  # type: ignore
    email_message.EmailMessage.update_forward_refs()  # type: ignore
    program.Program.update_forward_refs()  # type: ignore
    program_template.ProgramTemplate.update_forward_refs()  # type: ignore
    program_message.ProgramMessage.update_forward_refs()  # type: ignore
    form.Form.update_forward_refs()  # type: ignore
else:
    collection.Collection.model_rebuild(_parent_namespace_depth=0)
    view.View.model_rebuild(_parent_namespace_depth=0)
    inbox_conversation.InboxConversation.model_rebuild(_parent_namespace_depth=0)
    email_message.EmailMessage.model_rebuild(_parent_namespace_depth=0)
    program.Program.model_rebuild(_parent_namespace_depth=0)
    program_template.ProgramTemplate.model_rebuild(_parent_namespace_depth=0)
    program_message.ProgramMessage.model_rebuild(_parent_namespace_depth=0)
    form.Form.model_rebuild(_parent_namespace_depth=0)
