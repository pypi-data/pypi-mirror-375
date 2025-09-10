# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..types import inbox_message_list_params, inbox_message_retrieve_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..pagination import SyncCursorPage, AsyncCursorPage
from .._base_client import AsyncPaginator, make_request_options
from ..types.email_message import EmailMessage

__all__ = ["InboxMessagesResource", "AsyncInboxMessagesResource"]


class InboxMessagesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> InboxMessagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#accessing-raw-response-data-eg-headers
        """
        return InboxMessagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InboxMessagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#with_streaming_response
        """
        return InboxMessagesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        include: List[Literal["addresses", "attachments", "conversation"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EmailMessage:
        """
        Retrieves the details of an existing message.

        Args:
          include: Specifies which related objects to include in the response. Valid options are
              `addresses`, `attachments`, and `conversation`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/inbox_messages/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"include": include}, inbox_message_retrieve_params.InboxMessageRetrieveParams),
            ),
            cast_to=EmailMessage,
        )

    def list(
        self,
        *,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        filter: inbox_message_list_params.Filter | NotGiven = NOT_GIVEN,
        include: List[Literal["addresses", "attachments", "conversation"]] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[EmailMessage]:
        """
        Returns a list of messages.

        Args:
          after: When specified, returns results starting immediately after the item identified
              by this cursor. Use the cursor value from the previous response's metadata to
              fetch the next page of results.

          before: When specified, returns results starting immediately before the item identified
              by this cursor. Use the cursor value from the response's metadata to fetch the
              previous page of results.

          include: Specifies which related objects to include in the response. Valid options are
              `addresses`, `attachments`, and `conversation`.

          limit: Maximum number of items to return per page. Must be between 1 and 100. Defaults
              to 20 if not specified.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/inbox_messages",
            page=SyncCursorPage[EmailMessage],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "filter": filter,
                        "include": include,
                        "limit": limit,
                    },
                    inbox_message_list_params.InboxMessageListParams,
                ),
            ),
            model=EmailMessage,
        )


class AsyncInboxMessagesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncInboxMessagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncInboxMessagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInboxMessagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#with_streaming_response
        """
        return AsyncInboxMessagesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        include: List[Literal["addresses", "attachments", "conversation"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EmailMessage:
        """
        Retrieves the details of an existing message.

        Args:
          include: Specifies which related objects to include in the response. Valid options are
              `addresses`, `attachments`, and `conversation`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/inbox_messages/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"include": include}, inbox_message_retrieve_params.InboxMessageRetrieveParams
                ),
            ),
            cast_to=EmailMessage,
        )

    def list(
        self,
        *,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        filter: inbox_message_list_params.Filter | NotGiven = NOT_GIVEN,
        include: List[Literal["addresses", "attachments", "conversation"]] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[EmailMessage, AsyncCursorPage[EmailMessage]]:
        """
        Returns a list of messages.

        Args:
          after: When specified, returns results starting immediately after the item identified
              by this cursor. Use the cursor value from the previous response's metadata to
              fetch the next page of results.

          before: When specified, returns results starting immediately before the item identified
              by this cursor. Use the cursor value from the response's metadata to fetch the
              previous page of results.

          include: Specifies which related objects to include in the response. Valid options are
              `addresses`, `attachments`, and `conversation`.

          limit: Maximum number of items to return per page. Must be between 1 and 100. Defaults
              to 20 if not specified.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/inbox_messages",
            page=AsyncCursorPage[EmailMessage],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "filter": filter,
                        "include": include,
                        "limit": limit,
                    },
                    inbox_message_list_params.InboxMessageListParams,
                ),
            ),
            model=EmailMessage,
        )


class InboxMessagesResourceWithRawResponse:
    def __init__(self, inbox_messages: InboxMessagesResource) -> None:
        self._inbox_messages = inbox_messages

        self.retrieve = to_raw_response_wrapper(
            inbox_messages.retrieve,
        )
        self.list = to_raw_response_wrapper(
            inbox_messages.list,
        )


class AsyncInboxMessagesResourceWithRawResponse:
    def __init__(self, inbox_messages: AsyncInboxMessagesResource) -> None:
        self._inbox_messages = inbox_messages

        self.retrieve = async_to_raw_response_wrapper(
            inbox_messages.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            inbox_messages.list,
        )


class InboxMessagesResourceWithStreamingResponse:
    def __init__(self, inbox_messages: InboxMessagesResource) -> None:
        self._inbox_messages = inbox_messages

        self.retrieve = to_streamed_response_wrapper(
            inbox_messages.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            inbox_messages.list,
        )


class AsyncInboxMessagesResourceWithStreamingResponse:
    def __init__(self, inbox_messages: AsyncInboxMessagesResource) -> None:
        self._inbox_messages = inbox_messages

        self.retrieve = async_to_streamed_response_wrapper(
            inbox_messages.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            inbox_messages.list,
        )
