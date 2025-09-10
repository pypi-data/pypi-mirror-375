# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from moonbase import Moonbase, AsyncMoonbase
from tests.utils import assert_matches_type
from moonbase.types import Program
from moonbase.pagination import SyncCursorPage, AsyncCursorPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPrograms:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Moonbase) -> None:
        program = client.programs.retrieve(
            id="id",
        )
        assert_matches_type(Program, program, path=["response"])

    @parametrize
    def test_method_retrieve_with_all_params(self, client: Moonbase) -> None:
        program = client.programs.retrieve(
            id="id",
            include=["activity_metrics"],
        )
        assert_matches_type(Program, program, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Moonbase) -> None:
        response = client.programs.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        program = response.parse()
        assert_matches_type(Program, program, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Moonbase) -> None:
        with client.programs.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            program = response.parse()
            assert_matches_type(Program, program, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Moonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.programs.with_raw_response.retrieve(
                id="",
            )

    @parametrize
    def test_method_list(self, client: Moonbase) -> None:
        program = client.programs.list()
        assert_matches_type(SyncCursorPage[Program], program, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Moonbase) -> None:
        program = client.programs.list(
            after="after",
            before="before",
            limit=1,
        )
        assert_matches_type(SyncCursorPage[Program], program, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Moonbase) -> None:
        response = client.programs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        program = response.parse()
        assert_matches_type(SyncCursorPage[Program], program, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Moonbase) -> None:
        with client.programs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            program = response.parse()
            assert_matches_type(SyncCursorPage[Program], program, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPrograms:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMoonbase) -> None:
        program = await async_client.programs.retrieve(
            id="id",
        )
        assert_matches_type(Program, program, path=["response"])

    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncMoonbase) -> None:
        program = await async_client.programs.retrieve(
            id="id",
            include=["activity_metrics"],
        )
        assert_matches_type(Program, program, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.programs.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        program = await response.parse()
        assert_matches_type(Program, program, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMoonbase) -> None:
        async with async_client.programs.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            program = await response.parse()
            assert_matches_type(Program, program, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncMoonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.programs.with_raw_response.retrieve(
                id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncMoonbase) -> None:
        program = await async_client.programs.list()
        assert_matches_type(AsyncCursorPage[Program], program, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncMoonbase) -> None:
        program = await async_client.programs.list(
            after="after",
            before="before",
            limit=1,
        )
        assert_matches_type(AsyncCursorPage[Program], program, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.programs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        program = await response.parse()
        assert_matches_type(AsyncCursorPage[Program], program, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncMoonbase) -> None:
        async with async_client.programs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            program = await response.parse()
            assert_matches_type(AsyncCursorPage[Program], program, path=["response"])

        assert cast(Any, response.is_closed) is True
