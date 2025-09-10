# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..types import inbox_conversation_list_params, inbox_conversation_retrieve_params
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
from ..types.inbox_conversation import InboxConversation

__all__ = ["InboxConversationsResource", "AsyncInboxConversationsResource"]


class InboxConversationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> InboxConversationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#accessing-raw-response-data-eg-headers
        """
        return InboxConversationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InboxConversationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#with_streaming_response
        """
        return InboxConversationsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        include: List[Literal["inbox", "messages", "messages.addresses"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InboxConversation:
        """
        Retrieves the details of an existing conversation.

        Args:
          include: Specifies which related objects to include in the response. Valid options are
              `inbox`, `messages`, and `messages.addresses`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/inbox_conversations/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"include": include}, inbox_conversation_retrieve_params.InboxConversationRetrieveParams
                ),
            ),
            cast_to=InboxConversation,
        )

    def list(
        self,
        *,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        filter: inbox_conversation_list_params.Filter | NotGiven = NOT_GIVEN,
        include: List[Literal["inbox", "messages", "messages.addresses"]] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[InboxConversation]:
        """
        Returns a list of your conversations.

        Args:
          after: When specified, returns results starting immediately after the item identified
              by this cursor. Use the cursor value from the previous response's metadata to
              fetch the next page of results.

          before: When specified, returns results starting immediately before the item identified
              by this cursor. Use the cursor value from the response's metadata to fetch the
              previous page of results.

          include: Specifies which related objects to include in the response. Valid options are
              `inbox`, `messages`, and `messages.addresses`.

          limit: Maximum number of items to return per page. Must be between 1 and 100. Defaults
              to 20 if not specified.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/inbox_conversations",
            page=SyncCursorPage[InboxConversation],
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
                    inbox_conversation_list_params.InboxConversationListParams,
                ),
            ),
            model=InboxConversation,
        )


class AsyncInboxConversationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncInboxConversationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncInboxConversationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInboxConversationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#with_streaming_response
        """
        return AsyncInboxConversationsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        include: List[Literal["inbox", "messages", "messages.addresses"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InboxConversation:
        """
        Retrieves the details of an existing conversation.

        Args:
          include: Specifies which related objects to include in the response. Valid options are
              `inbox`, `messages`, and `messages.addresses`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/inbox_conversations/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"include": include}, inbox_conversation_retrieve_params.InboxConversationRetrieveParams
                ),
            ),
            cast_to=InboxConversation,
        )

    def list(
        self,
        *,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        filter: inbox_conversation_list_params.Filter | NotGiven = NOT_GIVEN,
        include: List[Literal["inbox", "messages", "messages.addresses"]] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[InboxConversation, AsyncCursorPage[InboxConversation]]:
        """
        Returns a list of your conversations.

        Args:
          after: When specified, returns results starting immediately after the item identified
              by this cursor. Use the cursor value from the previous response's metadata to
              fetch the next page of results.

          before: When specified, returns results starting immediately before the item identified
              by this cursor. Use the cursor value from the response's metadata to fetch the
              previous page of results.

          include: Specifies which related objects to include in the response. Valid options are
              `inbox`, `messages`, and `messages.addresses`.

          limit: Maximum number of items to return per page. Must be between 1 and 100. Defaults
              to 20 if not specified.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/inbox_conversations",
            page=AsyncCursorPage[InboxConversation],
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
                    inbox_conversation_list_params.InboxConversationListParams,
                ),
            ),
            model=InboxConversation,
        )


class InboxConversationsResourceWithRawResponse:
    def __init__(self, inbox_conversations: InboxConversationsResource) -> None:
        self._inbox_conversations = inbox_conversations

        self.retrieve = to_raw_response_wrapper(
            inbox_conversations.retrieve,
        )
        self.list = to_raw_response_wrapper(
            inbox_conversations.list,
        )


class AsyncInboxConversationsResourceWithRawResponse:
    def __init__(self, inbox_conversations: AsyncInboxConversationsResource) -> None:
        self._inbox_conversations = inbox_conversations

        self.retrieve = async_to_raw_response_wrapper(
            inbox_conversations.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            inbox_conversations.list,
        )


class InboxConversationsResourceWithStreamingResponse:
    def __init__(self, inbox_conversations: InboxConversationsResource) -> None:
        self._inbox_conversations = inbox_conversations

        self.retrieve = to_streamed_response_wrapper(
            inbox_conversations.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            inbox_conversations.list,
        )


class AsyncInboxConversationsResourceWithStreamingResponse:
    def __init__(self, inbox_conversations: AsyncInboxConversationsResource) -> None:
        self._inbox_conversations = inbox_conversations

        self.retrieve = async_to_streamed_response_wrapper(
            inbox_conversations.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            inbox_conversations.list,
        )
