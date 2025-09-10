# Shared Types

```python
from moonbase.types import Error, FormattedText, Pointer
```

# Funnels

Types:

```python
from moonbase.types import Funnel, FunnelStep
```

# Collections

Types:

```python
from moonbase.types import (
    BooleanField,
    BooleanValue,
    ChoiceField,
    ChoiceFieldOption,
    ChoiceValue,
    ChoiceValueParam,
    Collection,
    CollectionPointer,
    DateField,
    DateValue,
    DatetimeField,
    DatetimeValue,
    DomainField,
    DomainValue,
    EmailField,
    EmailValue,
    Field,
    FieldValue,
    FieldValueParam,
    FloatField,
    FloatValue,
    FunnelStepValue,
    FunnelStepValueParam,
    GeoField,
    GeoValue,
    IntegerField,
    IntegerValue,
    Item,
    ItemPointer,
    MonetaryField,
    MonetaryValue,
    MultiLineTextField,
    MultiLineTextValue,
    PercentageField,
    PercentageValue,
    RelationField,
    RelationValue,
    RelationValueParam,
    SingleLineTextField,
    SingleLineTextValue,
    SocialLinkedInField,
    SocialLinkedInValue,
    SocialXField,
    SocialXValue,
    StageField,
    TelephoneNumber,
    TelephoneNumberField,
    URLField,
    URLValue,
    Value,
    ValueParam,
)
```

Methods:

- <code title="get /collections/{id}">client.collections.<a href="./src/moonbase/resources/collections/collections.py">retrieve</a>(id, \*\*<a href="src/moonbase/types/collection_retrieve_params.py">params</a>) -> <a href="./src/moonbase/types/collection.py">Collection</a></code>
- <code title="get /collections">client.collections.<a href="./src/moonbase/resources/collections/collections.py">list</a>(\*\*<a href="src/moonbase/types/collection_list_params.py">params</a>) -> <a href="./src/moonbase/types/collection.py">SyncCursorPage[Collection]</a></code>

## Fields

Methods:

- <code title="get /collections/{collection_id}/fields/{id}">client.collections.fields.<a href="./src/moonbase/resources/collections/fields.py">retrieve</a>(id, \*, collection_id) -> <a href="./src/moonbase/types/field.py">Field</a></code>

## Items

Methods:

- <code title="post /collections/{collection_id}/items">client.collections.items.<a href="./src/moonbase/resources/collections/items.py">create</a>(collection_id, \*\*<a href="src/moonbase/types/collections/item_create_params.py">params</a>) -> <a href="./src/moonbase/types/item.py">Item</a></code>
- <code title="get /collections/{collection_id}/items/{id}">client.collections.items.<a href="./src/moonbase/resources/collections/items.py">retrieve</a>(id, \*, collection_id) -> <a href="./src/moonbase/types/item.py">Item</a></code>
- <code title="patch /collections/{collection_id}/items/{id}">client.collections.items.<a href="./src/moonbase/resources/collections/items.py">update</a>(id, \*, collection_id, \*\*<a href="src/moonbase/types/collections/item_update_params.py">params</a>) -> <a href="./src/moonbase/types/item.py">Item</a></code>
- <code title="get /collections/{collection_id}/items">client.collections.items.<a href="./src/moonbase/resources/collections/items.py">list</a>(collection_id, \*\*<a href="src/moonbase/types/collections/item_list_params.py">params</a>) -> <a href="./src/moonbase/types/item.py">SyncCursorPage[Item]</a></code>
- <code title="delete /collections/{collection_id}/items/{id}">client.collections.items.<a href="./src/moonbase/resources/collections/items.py">delete</a>(id, \*, collection_id) -> None</code>
- <code title="post /collections/{collection_id}/items/upsert">client.collections.items.<a href="./src/moonbase/resources/collections/items.py">upsert</a>(collection_id, \*\*<a href="src/moonbase/types/collections/item_upsert_params.py">params</a>) -> <a href="./src/moonbase/types/item.py">Item</a></code>

# Views

Types:

```python
from moonbase.types import View
```

Methods:

- <code title="get /views/{id}">client.views.<a href="./src/moonbase/resources/views/views.py">retrieve</a>(id, \*\*<a href="src/moonbase/types/view_retrieve_params.py">params</a>) -> <a href="./src/moonbase/types/view.py">View</a></code>

## Items

Methods:

- <code title="get /views/{id}/items">client.views.items.<a href="./src/moonbase/resources/views/items.py">list</a>(id, \*\*<a href="src/moonbase/types/views/item_list_params.py">params</a>) -> <a href="./src/moonbase/types/item.py">SyncCursorPage[Item]</a></code>

# Inboxes

Types:

```python
from moonbase.types import Inbox
```

Methods:

- <code title="get /inboxes/{id}">client.inboxes.<a href="./src/moonbase/resources/inboxes.py">retrieve</a>(id, \*\*<a href="src/moonbase/types/inbox_retrieve_params.py">params</a>) -> <a href="./src/moonbase/types/inbox.py">Inbox</a></code>
- <code title="get /inboxes">client.inboxes.<a href="./src/moonbase/resources/inboxes.py">list</a>(\*\*<a href="src/moonbase/types/inbox_list_params.py">params</a>) -> <a href="./src/moonbase/types/inbox.py">SyncCursorPage[Inbox]</a></code>

# InboxConversations

Types:

```python
from moonbase.types import InboxConversation
```

Methods:

- <code title="get /inbox_conversations/{id}">client.inbox_conversations.<a href="./src/moonbase/resources/inbox_conversations.py">retrieve</a>(id, \*\*<a href="src/moonbase/types/inbox_conversation_retrieve_params.py">params</a>) -> <a href="./src/moonbase/types/inbox_conversation.py">InboxConversation</a></code>
- <code title="get /inbox_conversations">client.inbox_conversations.<a href="./src/moonbase/resources/inbox_conversations.py">list</a>(\*\*<a href="src/moonbase/types/inbox_conversation_list_params.py">params</a>) -> <a href="./src/moonbase/types/inbox_conversation.py">SyncCursorPage[InboxConversation]</a></code>

# InboxMessages

Types:

```python
from moonbase.types import Address, EmailMessage
```

Methods:

- <code title="get /inbox_messages/{id}">client.inbox_messages.<a href="./src/moonbase/resources/inbox_messages.py">retrieve</a>(id, \*\*<a href="src/moonbase/types/inbox_message_retrieve_params.py">params</a>) -> <a href="./src/moonbase/types/email_message.py">EmailMessage</a></code>
- <code title="get /inbox_messages">client.inbox_messages.<a href="./src/moonbase/resources/inbox_messages.py">list</a>(\*\*<a href="src/moonbase/types/inbox_message_list_params.py">params</a>) -> <a href="./src/moonbase/types/email_message.py">SyncCursorPage[EmailMessage]</a></code>

# Tagsets

Types:

```python
from moonbase.types import Tagset
```

Methods:

- <code title="get /tagsets/{id}">client.tagsets.<a href="./src/moonbase/resources/tagsets.py">retrieve</a>(id) -> <a href="./src/moonbase/types/tagset.py">Tagset</a></code>
- <code title="get /tagsets">client.tagsets.<a href="./src/moonbase/resources/tagsets.py">list</a>(\*\*<a href="src/moonbase/types/tagset_list_params.py">params</a>) -> <a href="./src/moonbase/types/tagset.py">SyncCursorPage[Tagset]</a></code>

# Programs

Types:

```python
from moonbase.types import Program
```

Methods:

- <code title="get /programs/{id}">client.programs.<a href="./src/moonbase/resources/programs.py">retrieve</a>(id, \*\*<a href="src/moonbase/types/program_retrieve_params.py">params</a>) -> <a href="./src/moonbase/types/program.py">Program</a></code>
- <code title="get /programs">client.programs.<a href="./src/moonbase/resources/programs.py">list</a>(\*\*<a href="src/moonbase/types/program_list_params.py">params</a>) -> <a href="./src/moonbase/types/program.py">SyncCursorPage[Program]</a></code>

# ProgramTemplates

Types:

```python
from moonbase.types import ProgramTemplate
```

Methods:

- <code title="get /program_templates/{id}">client.program_templates.<a href="./src/moonbase/resources/program_templates.py">retrieve</a>(id, \*\*<a href="src/moonbase/types/program_template_retrieve_params.py">params</a>) -> <a href="./src/moonbase/types/program_template.py">ProgramTemplate</a></code>
- <code title="get /program_templates">client.program_templates.<a href="./src/moonbase/resources/program_templates.py">list</a>(\*\*<a href="src/moonbase/types/program_template_list_params.py">params</a>) -> <a href="./src/moonbase/types/program_template.py">SyncCursorPage[ProgramTemplate]</a></code>

# ProgramMessages

Types:

```python
from moonbase.types import ProgramMessage
```

Methods:

- <code title="post /program_messages">client.program_messages.<a href="./src/moonbase/resources/program_messages.py">send</a>(\*\*<a href="src/moonbase/types/program_message_send_params.py">params</a>) -> <a href="./src/moonbase/types/program_message.py">ProgramMessage</a></code>

# Forms

Types:

```python
from moonbase.types import Form
```

Methods:

- <code title="get /forms/{id}">client.forms.<a href="./src/moonbase/resources/forms.py">retrieve</a>(id) -> <a href="./src/moonbase/types/form.py">Form</a></code>
- <code title="get /forms">client.forms.<a href="./src/moonbase/resources/forms.py">list</a>(\*\*<a href="src/moonbase/types/form_list_params.py">params</a>) -> <a href="./src/moonbase/types/form.py">SyncCursorPage[Form]</a></code>

# Activities

Types:

```python
from moonbase.types import (
    Activity,
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
)
```

Methods:

- <code title="get /activities/{id}">client.activities.<a href="./src/moonbase/resources/activities.py">retrieve</a>(id) -> <a href="./src/moonbase/types/activity.py">Activity</a></code>
- <code title="get /activities">client.activities.<a href="./src/moonbase/resources/activities.py">list</a>(\*\*<a href="src/moonbase/types/activity_list_params.py">params</a>) -> <a href="./src/moonbase/types/activity.py">SyncCursorPage[Activity]</a></code>

# Calls

Types:

```python
from moonbase.types import Call
```

Methods:

- <code title="post /calls">client.calls.<a href="./src/moonbase/resources/calls.py">create</a>(\*\*<a href="src/moonbase/types/call_create_params.py">params</a>) -> <a href="./src/moonbase/types/call.py">Call</a></code>
- <code title="post /calls/upsert">client.calls.<a href="./src/moonbase/resources/calls.py">upsert</a>(\*\*<a href="src/moonbase/types/call_upsert_params.py">params</a>) -> <a href="./src/moonbase/types/call.py">Call</a></code>

# Files

Types:

```python
from moonbase.types import MoonbaseFile
```

Methods:

- <code title="get /files/{id}">client.files.<a href="./src/moonbase/resources/files.py">retrieve</a>(id) -> <a href="./src/moonbase/types/moonbase_file.py">MoonbaseFile</a></code>
- <code title="get /files">client.files.<a href="./src/moonbase/resources/files.py">list</a>(\*\*<a href="src/moonbase/types/file_list_params.py">params</a>) -> <a href="./src/moonbase/types/moonbase_file.py">SyncCursorPage[MoonbaseFile]</a></code>

# Meetings

Types:

```python
from moonbase.types import Attendee, Meeting, Organizer
```

Methods:

- <code title="get /meetings/{id}">client.meetings.<a href="./src/moonbase/resources/meetings.py">retrieve</a>(id, \*\*<a href="src/moonbase/types/meeting_retrieve_params.py">params</a>) -> <a href="./src/moonbase/types/meeting.py">Meeting</a></code>
- <code title="get /meetings">client.meetings.<a href="./src/moonbase/resources/meetings.py">list</a>(\*\*<a href="src/moonbase/types/meeting_list_params.py">params</a>) -> <a href="./src/moonbase/types/meeting.py">SyncCursorPage[Meeting]</a></code>

# Notes

Types:

```python
from moonbase.types import Note
```

Methods:

- <code title="get /notes/{id}">client.notes.<a href="./src/moonbase/resources/notes.py">retrieve</a>(id) -> <a href="./src/moonbase/types/note.py">Note</a></code>
- <code title="get /notes">client.notes.<a href="./src/moonbase/resources/notes.py">list</a>(\*\*<a href="src/moonbase/types/note_list_params.py">params</a>) -> <a href="./src/moonbase/types/note.py">SyncCursorPage[Note]</a></code>

# WebhookEndpoints

Types:

```python
from moonbase.types import Endpoint, Subscription
```

Methods:

- <code title="post /webhook_endpoints">client.webhook_endpoints.<a href="./src/moonbase/resources/webhook_endpoints.py">create</a>(\*\*<a href="src/moonbase/types/webhook_endpoint_create_params.py">params</a>) -> <a href="./src/moonbase/types/endpoint.py">Endpoint</a></code>
- <code title="get /webhook_endpoints/{id}">client.webhook_endpoints.<a href="./src/moonbase/resources/webhook_endpoints.py">retrieve</a>(id) -> <a href="./src/moonbase/types/endpoint.py">Endpoint</a></code>
- <code title="patch /webhook_endpoints/{id}">client.webhook_endpoints.<a href="./src/moonbase/resources/webhook_endpoints.py">update</a>(id, \*\*<a href="src/moonbase/types/webhook_endpoint_update_params.py">params</a>) -> <a href="./src/moonbase/types/endpoint.py">Endpoint</a></code>
- <code title="get /webhook_endpoints">client.webhook_endpoints.<a href="./src/moonbase/resources/webhook_endpoints.py">list</a>(\*\*<a href="src/moonbase/types/webhook_endpoint_list_params.py">params</a>) -> <a href="./src/moonbase/types/endpoint.py">SyncCursorPage[Endpoint]</a></code>
- <code title="delete /webhook_endpoints/{id}">client.webhook_endpoints.<a href="./src/moonbase/resources/webhook_endpoints.py">delete</a>(id) -> None</code>
