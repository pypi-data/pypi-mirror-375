# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

import httpx

from ..types import program_message_send_params
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
from .._base_client import make_request_options
from ..types.program_message import ProgramMessage

__all__ = ["ProgramMessagesResource", "AsyncProgramMessagesResource"]


class ProgramMessagesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ProgramMessagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ProgramMessagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProgramMessagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#with_streaming_response
        """
        return ProgramMessagesResourceWithStreamingResponse(self)

    def send(
        self,
        *,
        person: program_message_send_params.Person,
        program_template_id: str,
        custom_variables: Dict[str, object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProgramMessage:
        """
        Sends a message using a program template.

        Args:
          person: The person to send the message to.

          program_template_id: The ID of the `ProgramTemplate` to use for sending the message.

          custom_variables: Any custom Liquid variables to be interpolated into the message template.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/program_messages",
            body=maybe_transform(
                {
                    "person": person,
                    "program_template_id": program_template_id,
                    "custom_variables": custom_variables,
                },
                program_message_send_params.ProgramMessageSendParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProgramMessage,
        )


class AsyncProgramMessagesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncProgramMessagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncProgramMessagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProgramMessagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/moonbaseai/moonbase-sdk-python#with_streaming_response
        """
        return AsyncProgramMessagesResourceWithStreamingResponse(self)

    async def send(
        self,
        *,
        person: program_message_send_params.Person,
        program_template_id: str,
        custom_variables: Dict[str, object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProgramMessage:
        """
        Sends a message using a program template.

        Args:
          person: The person to send the message to.

          program_template_id: The ID of the `ProgramTemplate` to use for sending the message.

          custom_variables: Any custom Liquid variables to be interpolated into the message template.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/program_messages",
            body=await async_maybe_transform(
                {
                    "person": person,
                    "program_template_id": program_template_id,
                    "custom_variables": custom_variables,
                },
                program_message_send_params.ProgramMessageSendParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProgramMessage,
        )


class ProgramMessagesResourceWithRawResponse:
    def __init__(self, program_messages: ProgramMessagesResource) -> None:
        self._program_messages = program_messages

        self.send = to_raw_response_wrapper(
            program_messages.send,
        )


class AsyncProgramMessagesResourceWithRawResponse:
    def __init__(self, program_messages: AsyncProgramMessagesResource) -> None:
        self._program_messages = program_messages

        self.send = async_to_raw_response_wrapper(
            program_messages.send,
        )


class ProgramMessagesResourceWithStreamingResponse:
    def __init__(self, program_messages: ProgramMessagesResource) -> None:
        self._program_messages = program_messages

        self.send = to_streamed_response_wrapper(
            program_messages.send,
        )


class AsyncProgramMessagesResourceWithStreamingResponse:
    def __init__(self, program_messages: AsyncProgramMessagesResource) -> None:
        self._program_messages = program_messages

        self.send = async_to_streamed_response_wrapper(
            program_messages.send,
        )
