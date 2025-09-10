# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ..types import webhook_endpoint_list_params, webhook_endpoint_create_params, webhook_endpoint_update_params
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
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
from ..types.endpoint import Endpoint

__all__ = ["WebhookEndpointsResource", "AsyncWebhookEndpointsResource"]


class WebhookEndpointsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> WebhookEndpointsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#accessing-raw-response-data-eg-headers
        """
        return WebhookEndpointsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WebhookEndpointsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#with_streaming_response
        """
        return WebhookEndpointsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        status: Literal["disabled", "enabled"],
        url: str,
        subscriptions: Iterable[webhook_endpoint_create_params.Subscription] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Endpoint:
        """
        Create a new endpoint.

        Args:
          status: Indicates whether the endpoint is enabled.

          url: The HTTPS URL where webhook events will be sent.

          subscriptions: An array of event types that this endpoint should receive notifications for.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/webhook_endpoints",
            body=maybe_transform(
                {
                    "status": status,
                    "url": url,
                    "subscriptions": subscriptions,
                },
                webhook_endpoint_create_params.WebhookEndpointCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Endpoint,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Endpoint:
        """
        Retrieves the details of an existing endpoint.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/webhook_endpoints/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Endpoint,
        )

    def update(
        self,
        id: str,
        *,
        status: Literal["disabled", "enabled"] | NotGiven = NOT_GIVEN,
        subscriptions: Iterable[webhook_endpoint_update_params.Subscription] | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Endpoint:
        """
        Updates an endpoint.

        Args:
          status: Indicates whether the endpoint is enabled.

          subscriptions: An array of event types that this endpoint should receive notifications for.

          url: The HTTPS URL where webhook events will be sent.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/webhook_endpoints/{id}",
            body=maybe_transform(
                {
                    "status": status,
                    "subscriptions": subscriptions,
                    "url": url,
                },
                webhook_endpoint_update_params.WebhookEndpointUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Endpoint,
        )

    def list(
        self,
        *,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[Endpoint]:
        """
        Returns a list of endpoints.

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
            "/webhook_endpoints",
            page=SyncCursorPage[Endpoint],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "limit": limit,
                    },
                    webhook_endpoint_list_params.WebhookEndpointListParams,
                ),
            ),
            model=Endpoint,
        )

    def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Permanently deletes an endpoint.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/webhook_endpoints/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncWebhookEndpointsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncWebhookEndpointsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncWebhookEndpointsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWebhookEndpointsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#with_streaming_response
        """
        return AsyncWebhookEndpointsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        status: Literal["disabled", "enabled"],
        url: str,
        subscriptions: Iterable[webhook_endpoint_create_params.Subscription] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Endpoint:
        """
        Create a new endpoint.

        Args:
          status: Indicates whether the endpoint is enabled.

          url: The HTTPS URL where webhook events will be sent.

          subscriptions: An array of event types that this endpoint should receive notifications for.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/webhook_endpoints",
            body=await async_maybe_transform(
                {
                    "status": status,
                    "url": url,
                    "subscriptions": subscriptions,
                },
                webhook_endpoint_create_params.WebhookEndpointCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Endpoint,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Endpoint:
        """
        Retrieves the details of an existing endpoint.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/webhook_endpoints/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Endpoint,
        )

    async def update(
        self,
        id: str,
        *,
        status: Literal["disabled", "enabled"] | NotGiven = NOT_GIVEN,
        subscriptions: Iterable[webhook_endpoint_update_params.Subscription] | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Endpoint:
        """
        Updates an endpoint.

        Args:
          status: Indicates whether the endpoint is enabled.

          subscriptions: An array of event types that this endpoint should receive notifications for.

          url: The HTTPS URL where webhook events will be sent.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/webhook_endpoints/{id}",
            body=await async_maybe_transform(
                {
                    "status": status,
                    "subscriptions": subscriptions,
                    "url": url,
                },
                webhook_endpoint_update_params.WebhookEndpointUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Endpoint,
        )

    def list(
        self,
        *,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Endpoint, AsyncCursorPage[Endpoint]]:
        """
        Returns a list of endpoints.

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
            "/webhook_endpoints",
            page=AsyncCursorPage[Endpoint],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "limit": limit,
                    },
                    webhook_endpoint_list_params.WebhookEndpointListParams,
                ),
            ),
            model=Endpoint,
        )

    async def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Permanently deletes an endpoint.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/webhook_endpoints/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class WebhookEndpointsResourceWithRawResponse:
    def __init__(self, webhook_endpoints: WebhookEndpointsResource) -> None:
        self._webhook_endpoints = webhook_endpoints

        self.create = to_raw_response_wrapper(
            webhook_endpoints.create,
        )
        self.retrieve = to_raw_response_wrapper(
            webhook_endpoints.retrieve,
        )
        self.update = to_raw_response_wrapper(
            webhook_endpoints.update,
        )
        self.list = to_raw_response_wrapper(
            webhook_endpoints.list,
        )
        self.delete = to_raw_response_wrapper(
            webhook_endpoints.delete,
        )


class AsyncWebhookEndpointsResourceWithRawResponse:
    def __init__(self, webhook_endpoints: AsyncWebhookEndpointsResource) -> None:
        self._webhook_endpoints = webhook_endpoints

        self.create = async_to_raw_response_wrapper(
            webhook_endpoints.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            webhook_endpoints.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            webhook_endpoints.update,
        )
        self.list = async_to_raw_response_wrapper(
            webhook_endpoints.list,
        )
        self.delete = async_to_raw_response_wrapper(
            webhook_endpoints.delete,
        )


class WebhookEndpointsResourceWithStreamingResponse:
    def __init__(self, webhook_endpoints: WebhookEndpointsResource) -> None:
        self._webhook_endpoints = webhook_endpoints

        self.create = to_streamed_response_wrapper(
            webhook_endpoints.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            webhook_endpoints.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            webhook_endpoints.update,
        )
        self.list = to_streamed_response_wrapper(
            webhook_endpoints.list,
        )
        self.delete = to_streamed_response_wrapper(
            webhook_endpoints.delete,
        )


class AsyncWebhookEndpointsResourceWithStreamingResponse:
    def __init__(self, webhook_endpoints: AsyncWebhookEndpointsResource) -> None:
        self._webhook_endpoints = webhook_endpoints

        self.create = async_to_streamed_response_wrapper(
            webhook_endpoints.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            webhook_endpoints.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            webhook_endpoints.update,
        )
        self.list = async_to_streamed_response_wrapper(
            webhook_endpoints.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            webhook_endpoints.delete,
        )
