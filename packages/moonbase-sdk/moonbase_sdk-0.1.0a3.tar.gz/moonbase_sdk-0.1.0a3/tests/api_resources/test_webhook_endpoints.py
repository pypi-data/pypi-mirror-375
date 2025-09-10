# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from moonbase import Moonbase, AsyncMoonbase
from tests.utils import assert_matches_type
from moonbase.types import (
    Endpoint,
)
from moonbase.pagination import SyncCursorPage, AsyncCursorPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWebhookEndpoints:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Moonbase) -> None:
        webhook_endpoint = client.webhook_endpoints.create(
            status="enabled",
            url="https://example.com/webhook",
        )
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Moonbase) -> None:
        webhook_endpoint = client.webhook_endpoints.create(
            status="enabled",
            url="https://example.com/webhook",
            subscriptions=[{"event_type": "activity/item_created"}, {"event_type": "activity/item_mentioned"}],
        )
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Moonbase) -> None:
        response = client.webhook_endpoints.with_raw_response.create(
            status="enabled",
            url="https://example.com/webhook",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook_endpoint = response.parse()
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Moonbase) -> None:
        with client.webhook_endpoints.with_streaming_response.create(
            status="enabled",
            url="https://example.com/webhook",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook_endpoint = response.parse()
            assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Moonbase) -> None:
        webhook_endpoint = client.webhook_endpoints.retrieve(
            "id",
        )
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Moonbase) -> None:
        response = client.webhook_endpoints.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook_endpoint = response.parse()
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Moonbase) -> None:
        with client.webhook_endpoints.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook_endpoint = response.parse()
            assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Moonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.webhook_endpoints.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: Moonbase) -> None:
        webhook_endpoint = client.webhook_endpoints.update(
            id="id",
        )
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Moonbase) -> None:
        webhook_endpoint = client.webhook_endpoints.update(
            id="id",
            status="disabled",
            subscriptions=[
                {
                    "event_type": "activity/call_occurred",
                    "id": "id",
                }
            ],
            url="https://updated.example.com",
        )
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Moonbase) -> None:
        response = client.webhook_endpoints.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook_endpoint = response.parse()
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Moonbase) -> None:
        with client.webhook_endpoints.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook_endpoint = response.parse()
            assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Moonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.webhook_endpoints.with_raw_response.update(
                id="",
            )

    @parametrize
    def test_method_list(self, client: Moonbase) -> None:
        webhook_endpoint = client.webhook_endpoints.list()
        assert_matches_type(SyncCursorPage[Endpoint], webhook_endpoint, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Moonbase) -> None:
        webhook_endpoint = client.webhook_endpoints.list(
            after="after",
            before="before",
            limit=1,
        )
        assert_matches_type(SyncCursorPage[Endpoint], webhook_endpoint, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Moonbase) -> None:
        response = client.webhook_endpoints.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook_endpoint = response.parse()
        assert_matches_type(SyncCursorPage[Endpoint], webhook_endpoint, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Moonbase) -> None:
        with client.webhook_endpoints.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook_endpoint = response.parse()
            assert_matches_type(SyncCursorPage[Endpoint], webhook_endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: Moonbase) -> None:
        webhook_endpoint = client.webhook_endpoints.delete(
            "id",
        )
        assert webhook_endpoint is None

    @parametrize
    def test_raw_response_delete(self, client: Moonbase) -> None:
        response = client.webhook_endpoints.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook_endpoint = response.parse()
        assert webhook_endpoint is None

    @parametrize
    def test_streaming_response_delete(self, client: Moonbase) -> None:
        with client.webhook_endpoints.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook_endpoint = response.parse()
            assert webhook_endpoint is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Moonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.webhook_endpoints.with_raw_response.delete(
                "",
            )


class TestAsyncWebhookEndpoints:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncMoonbase) -> None:
        webhook_endpoint = await async_client.webhook_endpoints.create(
            status="enabled",
            url="https://example.com/webhook",
        )
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMoonbase) -> None:
        webhook_endpoint = await async_client.webhook_endpoints.create(
            status="enabled",
            url="https://example.com/webhook",
            subscriptions=[{"event_type": "activity/item_created"}, {"event_type": "activity/item_mentioned"}],
        )
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.webhook_endpoints.with_raw_response.create(
            status="enabled",
            url="https://example.com/webhook",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook_endpoint = await response.parse()
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMoonbase) -> None:
        async with async_client.webhook_endpoints.with_streaming_response.create(
            status="enabled",
            url="https://example.com/webhook",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook_endpoint = await response.parse()
            assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMoonbase) -> None:
        webhook_endpoint = await async_client.webhook_endpoints.retrieve(
            "id",
        )
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.webhook_endpoints.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook_endpoint = await response.parse()
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMoonbase) -> None:
        async with async_client.webhook_endpoints.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook_endpoint = await response.parse()
            assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncMoonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.webhook_endpoints.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncMoonbase) -> None:
        webhook_endpoint = await async_client.webhook_endpoints.update(
            id="id",
        )
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMoonbase) -> None:
        webhook_endpoint = await async_client.webhook_endpoints.update(
            id="id",
            status="disabled",
            subscriptions=[
                {
                    "event_type": "activity/call_occurred",
                    "id": "id",
                }
            ],
            url="https://updated.example.com",
        )
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.webhook_endpoints.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook_endpoint = await response.parse()
        assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMoonbase) -> None:
        async with async_client.webhook_endpoints.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook_endpoint = await response.parse()
            assert_matches_type(Endpoint, webhook_endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncMoonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.webhook_endpoints.with_raw_response.update(
                id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncMoonbase) -> None:
        webhook_endpoint = await async_client.webhook_endpoints.list()
        assert_matches_type(AsyncCursorPage[Endpoint], webhook_endpoint, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncMoonbase) -> None:
        webhook_endpoint = await async_client.webhook_endpoints.list(
            after="after",
            before="before",
            limit=1,
        )
        assert_matches_type(AsyncCursorPage[Endpoint], webhook_endpoint, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.webhook_endpoints.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook_endpoint = await response.parse()
        assert_matches_type(AsyncCursorPage[Endpoint], webhook_endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncMoonbase) -> None:
        async with async_client.webhook_endpoints.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook_endpoint = await response.parse()
            assert_matches_type(AsyncCursorPage[Endpoint], webhook_endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncMoonbase) -> None:
        webhook_endpoint = await async_client.webhook_endpoints.delete(
            "id",
        )
        assert webhook_endpoint is None

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.webhook_endpoints.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook_endpoint = await response.parse()
        assert webhook_endpoint is None

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMoonbase) -> None:
        async with async_client.webhook_endpoints.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook_endpoint = await response.parse()
            assert webhook_endpoint is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMoonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.webhook_endpoints.with_raw_response.delete(
                "",
            )
