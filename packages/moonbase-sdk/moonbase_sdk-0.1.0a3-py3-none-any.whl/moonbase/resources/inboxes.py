# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import inbox_list_params, inbox_retrieve_params
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
from ..types.inbox import Inbox
from .._base_client import AsyncPaginator, make_request_options

__all__ = ["InboxesResource", "AsyncInboxesResource"]


class InboxesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> InboxesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#accessing-raw-response-data-eg-headers
        """
        return InboxesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InboxesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#with_streaming_response
        """
        return InboxesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        include: Literal["tagset"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Inbox:
        """
        Retrieves the details of an existing inbox.

        Args:
          include: Specifies which related objects to include in the response. Valid option is
              `tagset`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/inboxes/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"include": include}, inbox_retrieve_params.InboxRetrieveParams),
            ),
            cast_to=Inbox,
        )

    def list(
        self,
        *,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        include: Literal["tagset"] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[Inbox]:
        """
        Returns a list of shared inboxes.

        Args:
          after: When specified, returns results starting immediately after the item identified
              by this cursor. Use the cursor value from the previous response's metadata to
              fetch the next page of results.

          before: When specified, returns results starting immediately before the item identified
              by this cursor. Use the cursor value from the response's metadata to fetch the
              previous page of results.

          limit: Maximum number of items to return per page. Must be between 1 and 100. Defaults
              to 20 if not specified.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/inboxes",
            page=SyncCursorPage[Inbox],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "include": include,
                        "limit": limit,
                    },
                    inbox_list_params.InboxListParams,
                ),
            ),
            model=Inbox,
        )


class AsyncInboxesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncInboxesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncInboxesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInboxesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#with_streaming_response
        """
        return AsyncInboxesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        include: Literal["tagset"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Inbox:
        """
        Retrieves the details of an existing inbox.

        Args:
          include: Specifies which related objects to include in the response. Valid option is
              `tagset`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/inboxes/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"include": include}, inbox_retrieve_params.InboxRetrieveParams),
            ),
            cast_to=Inbox,
        )

    def list(
        self,
        *,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        include: Literal["tagset"] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Inbox, AsyncCursorPage[Inbox]]:
        """
        Returns a list of shared inboxes.

        Args:
          after: When specified, returns results starting immediately after the item identified
              by this cursor. Use the cursor value from the previous response's metadata to
              fetch the next page of results.

          before: When specified, returns results starting immediately before the item identified
              by this cursor. Use the cursor value from the response's metadata to fetch the
              previous page of results.

          limit: Maximum number of items to return per page. Must be between 1 and 100. Defaults
              to 20 if not specified.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/inboxes",
            page=AsyncCursorPage[Inbox],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "include": include,
                        "limit": limit,
                    },
                    inbox_list_params.InboxListParams,
                ),
            ),
            model=Inbox,
        )


class InboxesResourceWithRawResponse:
    def __init__(self, inboxes: InboxesResource) -> None:
        self._inboxes = inboxes

        self.retrieve = to_raw_response_wrapper(
            inboxes.retrieve,
        )
        self.list = to_raw_response_wrapper(
            inboxes.list,
        )


class AsyncInboxesResourceWithRawResponse:
    def __init__(self, inboxes: AsyncInboxesResource) -> None:
        self._inboxes = inboxes

        self.retrieve = async_to_raw_response_wrapper(
            inboxes.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            inboxes.list,
        )


class InboxesResourceWithStreamingResponse:
    def __init__(self, inboxes: InboxesResource) -> None:
        self._inboxes = inboxes

        self.retrieve = to_streamed_response_wrapper(
            inboxes.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            inboxes.list,
        )


class AsyncInboxesResourceWithStreamingResponse:
    def __init__(self, inboxes: AsyncInboxesResource) -> None:
        self._inboxes = inboxes

        self.retrieve = async_to_streamed_response_wrapper(
            inboxes.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            inboxes.list,
        )
