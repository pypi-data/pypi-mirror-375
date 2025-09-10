# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from moonbase import Moonbase, AsyncMoonbase
from tests.utils import assert_matches_type
from moonbase.types import ProgramMessage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProgramMessages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_send(self, client: Moonbase) -> None:
        program_message = client.program_messages.send(
            person={"email": "person-18@example-18.com"},
            program_template_id="1CLJt2v1MsDbov8DBEEeWH",
        )
        assert_matches_type(ProgramMessage, program_message, path=["response"])

    @parametrize
    def test_method_send_with_all_params(self, client: Moonbase) -> None:
        program_message = client.program_messages.send(
            person={"email": "person-18@example-18.com"},
            program_template_id="1CLJt2v1MsDbov8DBEEeWH",
            custom_variables={"coupon_code": "bar"},
        )
        assert_matches_type(ProgramMessage, program_message, path=["response"])

    @parametrize
    def test_raw_response_send(self, client: Moonbase) -> None:
        response = client.program_messages.with_raw_response.send(
            person={"email": "person-18@example-18.com"},
            program_template_id="1CLJt2v1MsDbov8DBEEeWH",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        program_message = response.parse()
        assert_matches_type(ProgramMessage, program_message, path=["response"])

    @parametrize
    def test_streaming_response_send(self, client: Moonbase) -> None:
        with client.program_messages.with_streaming_response.send(
            person={"email": "person-18@example-18.com"},
            program_template_id="1CLJt2v1MsDbov8DBEEeWH",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            program_message = response.parse()
            assert_matches_type(ProgramMessage, program_message, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncProgramMessages:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_send(self, async_client: AsyncMoonbase) -> None:
        program_message = await async_client.program_messages.send(
            person={"email": "person-18@example-18.com"},
            program_template_id="1CLJt2v1MsDbov8DBEEeWH",
        )
        assert_matches_type(ProgramMessage, program_message, path=["response"])

    @parametrize
    async def test_method_send_with_all_params(self, async_client: AsyncMoonbase) -> None:
        program_message = await async_client.program_messages.send(
            person={"email": "person-18@example-18.com"},
            program_template_id="1CLJt2v1MsDbov8DBEEeWH",
            custom_variables={"coupon_code": "bar"},
        )
        assert_matches_type(ProgramMessage, program_message, path=["response"])

    @parametrize
    async def test_raw_response_send(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.program_messages.with_raw_response.send(
            person={"email": "person-18@example-18.com"},
            program_template_id="1CLJt2v1MsDbov8DBEEeWH",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        program_message = await response.parse()
        assert_matches_type(ProgramMessage, program_message, path=["response"])

    @parametrize
    async def test_streaming_response_send(self, async_client: AsyncMoonbase) -> None:
        async with async_client.program_messages.with_streaming_response.send(
            person={"email": "person-18@example-18.com"},
            program_template_id="1CLJt2v1MsDbov8DBEEeWH",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            program_message = await response.parse()
            assert_matches_type(ProgramMessage, program_message, path=["response"])

        assert cast(Any, response.is_closed) is True
