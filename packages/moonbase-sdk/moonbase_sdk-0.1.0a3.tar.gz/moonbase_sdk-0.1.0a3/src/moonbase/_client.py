# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import (
    calls,
    files,
    forms,
    notes,
    inboxes,
    tagsets,
    meetings,
    programs,
    activities,
    inbox_messages,
    program_messages,
    program_templates,
    webhook_endpoints,
    inbox_conversations,
)
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import MoonbaseError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.views import views
from .resources.collections import collections

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Moonbase",
    "AsyncMoonbase",
    "Client",
    "AsyncClient",
]


class Moonbase(SyncAPIClient):
    collections: collections.CollectionsResource
    views: views.ViewsResource
    inboxes: inboxes.InboxesResource
    inbox_conversations: inbox_conversations.InboxConversationsResource
    inbox_messages: inbox_messages.InboxMessagesResource
    tagsets: tagsets.TagsetsResource
    programs: programs.ProgramsResource
    program_templates: program_templates.ProgramTemplatesResource
    program_messages: program_messages.ProgramMessagesResource
    forms: forms.FormsResource
    activities: activities.ActivitiesResource
    calls: calls.CallsResource
    files: files.FilesResource
    meetings: meetings.MeetingsResource
    notes: notes.NotesResource
    webhook_endpoints: webhook_endpoints.WebhookEndpointsResource
    with_raw_response: MoonbaseWithRawResponse
    with_streaming_response: MoonbaseWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Moonbase client instance.

        This automatically infers the `api_key` argument from the `MOONBASE_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("MOONBASE_API_KEY")
        if api_key is None:
            raise MoonbaseError(
                "The api_key client option must be set either by passing api_key to the client or by setting the MOONBASE_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("MOONBASE_BASE_URL")
        if base_url is None:
            base_url = f"https://api.moonbase.ai/v0"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.collections = collections.CollectionsResource(self)
        self.views = views.ViewsResource(self)
        self.inboxes = inboxes.InboxesResource(self)
        self.inbox_conversations = inbox_conversations.InboxConversationsResource(self)
        self.inbox_messages = inbox_messages.InboxMessagesResource(self)
        self.tagsets = tagsets.TagsetsResource(self)
        self.programs = programs.ProgramsResource(self)
        self.program_templates = program_templates.ProgramTemplatesResource(self)
        self.program_messages = program_messages.ProgramMessagesResource(self)
        self.forms = forms.FormsResource(self)
        self.activities = activities.ActivitiesResource(self)
        self.calls = calls.CallsResource(self)
        self.files = files.FilesResource(self)
        self.meetings = meetings.MeetingsResource(self)
        self.notes = notes.NotesResource(self)
        self.webhook_endpoints = webhook_endpoints.WebhookEndpointsResource(self)
        self.with_raw_response = MoonbaseWithRawResponse(self)
        self.with_streaming_response = MoonbaseWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="brackets")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncMoonbase(AsyncAPIClient):
    collections: collections.AsyncCollectionsResource
    views: views.AsyncViewsResource
    inboxes: inboxes.AsyncInboxesResource
    inbox_conversations: inbox_conversations.AsyncInboxConversationsResource
    inbox_messages: inbox_messages.AsyncInboxMessagesResource
    tagsets: tagsets.AsyncTagsetsResource
    programs: programs.AsyncProgramsResource
    program_templates: program_templates.AsyncProgramTemplatesResource
    program_messages: program_messages.AsyncProgramMessagesResource
    forms: forms.AsyncFormsResource
    activities: activities.AsyncActivitiesResource
    calls: calls.AsyncCallsResource
    files: files.AsyncFilesResource
    meetings: meetings.AsyncMeetingsResource
    notes: notes.AsyncNotesResource
    webhook_endpoints: webhook_endpoints.AsyncWebhookEndpointsResource
    with_raw_response: AsyncMoonbaseWithRawResponse
    with_streaming_response: AsyncMoonbaseWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncMoonbase client instance.

        This automatically infers the `api_key` argument from the `MOONBASE_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("MOONBASE_API_KEY")
        if api_key is None:
            raise MoonbaseError(
                "The api_key client option must be set either by passing api_key to the client or by setting the MOONBASE_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("MOONBASE_BASE_URL")
        if base_url is None:
            base_url = f"https://api.moonbase.ai/v0"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.collections = collections.AsyncCollectionsResource(self)
        self.views = views.AsyncViewsResource(self)
        self.inboxes = inboxes.AsyncInboxesResource(self)
        self.inbox_conversations = inbox_conversations.AsyncInboxConversationsResource(self)
        self.inbox_messages = inbox_messages.AsyncInboxMessagesResource(self)
        self.tagsets = tagsets.AsyncTagsetsResource(self)
        self.programs = programs.AsyncProgramsResource(self)
        self.program_templates = program_templates.AsyncProgramTemplatesResource(self)
        self.program_messages = program_messages.AsyncProgramMessagesResource(self)
        self.forms = forms.AsyncFormsResource(self)
        self.activities = activities.AsyncActivitiesResource(self)
        self.calls = calls.AsyncCallsResource(self)
        self.files = files.AsyncFilesResource(self)
        self.meetings = meetings.AsyncMeetingsResource(self)
        self.notes = notes.AsyncNotesResource(self)
        self.webhook_endpoints = webhook_endpoints.AsyncWebhookEndpointsResource(self)
        self.with_raw_response = AsyncMoonbaseWithRawResponse(self)
        self.with_streaming_response = AsyncMoonbaseWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="brackets")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class MoonbaseWithRawResponse:
    def __init__(self, client: Moonbase) -> None:
        self.collections = collections.CollectionsResourceWithRawResponse(client.collections)
        self.views = views.ViewsResourceWithRawResponse(client.views)
        self.inboxes = inboxes.InboxesResourceWithRawResponse(client.inboxes)
        self.inbox_conversations = inbox_conversations.InboxConversationsResourceWithRawResponse(
            client.inbox_conversations
        )
        self.inbox_messages = inbox_messages.InboxMessagesResourceWithRawResponse(client.inbox_messages)
        self.tagsets = tagsets.TagsetsResourceWithRawResponse(client.tagsets)
        self.programs = programs.ProgramsResourceWithRawResponse(client.programs)
        self.program_templates = program_templates.ProgramTemplatesResourceWithRawResponse(client.program_templates)
        self.program_messages = program_messages.ProgramMessagesResourceWithRawResponse(client.program_messages)
        self.forms = forms.FormsResourceWithRawResponse(client.forms)
        self.activities = activities.ActivitiesResourceWithRawResponse(client.activities)
        self.calls = calls.CallsResourceWithRawResponse(client.calls)
        self.files = files.FilesResourceWithRawResponse(client.files)
        self.meetings = meetings.MeetingsResourceWithRawResponse(client.meetings)
        self.notes = notes.NotesResourceWithRawResponse(client.notes)
        self.webhook_endpoints = webhook_endpoints.WebhookEndpointsResourceWithRawResponse(client.webhook_endpoints)


class AsyncMoonbaseWithRawResponse:
    def __init__(self, client: AsyncMoonbase) -> None:
        self.collections = collections.AsyncCollectionsResourceWithRawResponse(client.collections)
        self.views = views.AsyncViewsResourceWithRawResponse(client.views)
        self.inboxes = inboxes.AsyncInboxesResourceWithRawResponse(client.inboxes)
        self.inbox_conversations = inbox_conversations.AsyncInboxConversationsResourceWithRawResponse(
            client.inbox_conversations
        )
        self.inbox_messages = inbox_messages.AsyncInboxMessagesResourceWithRawResponse(client.inbox_messages)
        self.tagsets = tagsets.AsyncTagsetsResourceWithRawResponse(client.tagsets)
        self.programs = programs.AsyncProgramsResourceWithRawResponse(client.programs)
        self.program_templates = program_templates.AsyncProgramTemplatesResourceWithRawResponse(
            client.program_templates
        )
        self.program_messages = program_messages.AsyncProgramMessagesResourceWithRawResponse(client.program_messages)
        self.forms = forms.AsyncFormsResourceWithRawResponse(client.forms)
        self.activities = activities.AsyncActivitiesResourceWithRawResponse(client.activities)
        self.calls = calls.AsyncCallsResourceWithRawResponse(client.calls)
        self.files = files.AsyncFilesResourceWithRawResponse(client.files)
        self.meetings = meetings.AsyncMeetingsResourceWithRawResponse(client.meetings)
        self.notes = notes.AsyncNotesResourceWithRawResponse(client.notes)
        self.webhook_endpoints = webhook_endpoints.AsyncWebhookEndpointsResourceWithRawResponse(
            client.webhook_endpoints
        )


class MoonbaseWithStreamedResponse:
    def __init__(self, client: Moonbase) -> None:
        self.collections = collections.CollectionsResourceWithStreamingResponse(client.collections)
        self.views = views.ViewsResourceWithStreamingResponse(client.views)
        self.inboxes = inboxes.InboxesResourceWithStreamingResponse(client.inboxes)
        self.inbox_conversations = inbox_conversations.InboxConversationsResourceWithStreamingResponse(
            client.inbox_conversations
        )
        self.inbox_messages = inbox_messages.InboxMessagesResourceWithStreamingResponse(client.inbox_messages)
        self.tagsets = tagsets.TagsetsResourceWithStreamingResponse(client.tagsets)
        self.programs = programs.ProgramsResourceWithStreamingResponse(client.programs)
        self.program_templates = program_templates.ProgramTemplatesResourceWithStreamingResponse(
            client.program_templates
        )
        self.program_messages = program_messages.ProgramMessagesResourceWithStreamingResponse(client.program_messages)
        self.forms = forms.FormsResourceWithStreamingResponse(client.forms)
        self.activities = activities.ActivitiesResourceWithStreamingResponse(client.activities)
        self.calls = calls.CallsResourceWithStreamingResponse(client.calls)
        self.files = files.FilesResourceWithStreamingResponse(client.files)
        self.meetings = meetings.MeetingsResourceWithStreamingResponse(client.meetings)
        self.notes = notes.NotesResourceWithStreamingResponse(client.notes)
        self.webhook_endpoints = webhook_endpoints.WebhookEndpointsResourceWithStreamingResponse(
            client.webhook_endpoints
        )


class AsyncMoonbaseWithStreamedResponse:
    def __init__(self, client: AsyncMoonbase) -> None:
        self.collections = collections.AsyncCollectionsResourceWithStreamingResponse(client.collections)
        self.views = views.AsyncViewsResourceWithStreamingResponse(client.views)
        self.inboxes = inboxes.AsyncInboxesResourceWithStreamingResponse(client.inboxes)
        self.inbox_conversations = inbox_conversations.AsyncInboxConversationsResourceWithStreamingResponse(
            client.inbox_conversations
        )
        self.inbox_messages = inbox_messages.AsyncInboxMessagesResourceWithStreamingResponse(client.inbox_messages)
        self.tagsets = tagsets.AsyncTagsetsResourceWithStreamingResponse(client.tagsets)
        self.programs = programs.AsyncProgramsResourceWithStreamingResponse(client.programs)
        self.program_templates = program_templates.AsyncProgramTemplatesResourceWithStreamingResponse(
            client.program_templates
        )
        self.program_messages = program_messages.AsyncProgramMessagesResourceWithStreamingResponse(
            client.program_messages
        )
        self.forms = forms.AsyncFormsResourceWithStreamingResponse(client.forms)
        self.activities = activities.AsyncActivitiesResourceWithStreamingResponse(client.activities)
        self.calls = calls.AsyncCallsResourceWithStreamingResponse(client.calls)
        self.files = files.AsyncFilesResourceWithStreamingResponse(client.files)
        self.meetings = meetings.AsyncMeetingsResourceWithStreamingResponse(client.meetings)
        self.notes = notes.AsyncNotesResourceWithStreamingResponse(client.notes)
        self.webhook_endpoints = webhook_endpoints.AsyncWebhookEndpointsResourceWithStreamingResponse(
            client.webhook_endpoints
        )


Client = Moonbase

AsyncClient = AsyncMoonbase
