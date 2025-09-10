# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from moonbase import Moonbase, AsyncMoonbase
from tests.utils import assert_matches_type
from moonbase.types import Item
from moonbase.pagination import SyncCursorPage, AsyncCursorPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestItems:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Moonbase) -> None:
        item = client.collections.items.create(
            collection_id="collection_id",
            values={
                "name": {
                    "data": "Aperture Science",
                    "type": "value/text/single_line",
                },
                "ceo": {
                    "data": {
                        "id": "1CLJt2v2rARKGD4MLziBCw",
                        "type": "item",
                    },
                    "type": "value/relation",
                },
            },
        )
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Moonbase) -> None:
        response = client.collections.items.with_raw_response.create(
            collection_id="collection_id",
            values={
                "name": {
                    "data": "Aperture Science",
                    "type": "value/text/single_line",
                },
                "ceo": {
                    "data": {
                        "id": "1CLJt2v2rARKGD4MLziBCw",
                        "type": "item",
                    },
                    "type": "value/relation",
                },
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = response.parse()
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Moonbase) -> None:
        with client.collections.items.with_streaming_response.create(
            collection_id="collection_id",
            values={
                "name": {
                    "data": "Aperture Science",
                    "type": "value/text/single_line",
                },
                "ceo": {
                    "data": {
                        "id": "1CLJt2v2rARKGD4MLziBCw",
                        "type": "item",
                    },
                    "type": "value/relation",
                },
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = response.parse()
            assert_matches_type(Item, item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: Moonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `collection_id` but received ''"):
            client.collections.items.with_raw_response.create(
                collection_id="",
                values={
                    "name": {
                        "data": "Aperture Science",
                        "type": "value/text/single_line",
                    },
                    "ceo": {
                        "data": {
                            "id": "1CLJt2v2rARKGD4MLziBCw",
                            "type": "item",
                        },
                        "type": "value/relation",
                    },
                },
            )

    @parametrize
    def test_method_retrieve(self, client: Moonbase) -> None:
        item = client.collections.items.retrieve(
            id="id",
            collection_id="collection_id",
        )
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Moonbase) -> None:
        response = client.collections.items.with_raw_response.retrieve(
            id="id",
            collection_id="collection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = response.parse()
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Moonbase) -> None:
        with client.collections.items.with_streaming_response.retrieve(
            id="id",
            collection_id="collection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = response.parse()
            assert_matches_type(Item, item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Moonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `collection_id` but received ''"):
            client.collections.items.with_raw_response.retrieve(
                id="id",
                collection_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.collections.items.with_raw_response.retrieve(
                id="",
                collection_id="collection_id",
            )

    @parametrize
    def test_method_update(self, client: Moonbase) -> None:
        item = client.collections.items.update(
            id="id",
            collection_id="collection_id",
            values={
                "name": {
                    "data": "Jony Appleseed",
                    "type": "value/text/single_line",
                }
            },
        )
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Moonbase) -> None:
        item = client.collections.items.update(
            id="id",
            collection_id="collection_id",
            values={
                "name": {
                    "data": "Jony Appleseed",
                    "type": "value/text/single_line",
                }
            },
            update_many_strategy="replace",
            update_one_strategy="replace",
        )
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Moonbase) -> None:
        response = client.collections.items.with_raw_response.update(
            id="id",
            collection_id="collection_id",
            values={
                "name": {
                    "data": "Jony Appleseed",
                    "type": "value/text/single_line",
                }
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = response.parse()
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Moonbase) -> None:
        with client.collections.items.with_streaming_response.update(
            id="id",
            collection_id="collection_id",
            values={
                "name": {
                    "data": "Jony Appleseed",
                    "type": "value/text/single_line",
                }
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = response.parse()
            assert_matches_type(Item, item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Moonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `collection_id` but received ''"):
            client.collections.items.with_raw_response.update(
                id="id",
                collection_id="",
                values={
                    "name": {
                        "data": "Jony Appleseed",
                        "type": "value/text/single_line",
                    }
                },
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.collections.items.with_raw_response.update(
                id="",
                collection_id="collection_id",
                values={
                    "name": {
                        "data": "Jony Appleseed",
                        "type": "value/text/single_line",
                    }
                },
            )

    @parametrize
    def test_method_list(self, client: Moonbase) -> None:
        item = client.collections.items.list(
            collection_id="collection_id",
        )
        assert_matches_type(SyncCursorPage[Item], item, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Moonbase) -> None:
        item = client.collections.items.list(
            collection_id="collection_id",
            after="after",
            before="before",
            limit=1,
        )
        assert_matches_type(SyncCursorPage[Item], item, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Moonbase) -> None:
        response = client.collections.items.with_raw_response.list(
            collection_id="collection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = response.parse()
        assert_matches_type(SyncCursorPage[Item], item, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Moonbase) -> None:
        with client.collections.items.with_streaming_response.list(
            collection_id="collection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = response.parse()
            assert_matches_type(SyncCursorPage[Item], item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Moonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `collection_id` but received ''"):
            client.collections.items.with_raw_response.list(
                collection_id="",
            )

    @parametrize
    def test_method_delete(self, client: Moonbase) -> None:
        item = client.collections.items.delete(
            id="id",
            collection_id="collection_id",
        )
        assert item is None

    @parametrize
    def test_raw_response_delete(self, client: Moonbase) -> None:
        response = client.collections.items.with_raw_response.delete(
            id="id",
            collection_id="collection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = response.parse()
        assert item is None

    @parametrize
    def test_streaming_response_delete(self, client: Moonbase) -> None:
        with client.collections.items.with_streaming_response.delete(
            id="id",
            collection_id="collection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = response.parse()
            assert item is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Moonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `collection_id` but received ''"):
            client.collections.items.with_raw_response.delete(
                id="id",
                collection_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.collections.items.with_raw_response.delete(
                id="",
                collection_id="collection_id",
            )

    @parametrize
    def test_method_upsert(self, client: Moonbase) -> None:
        item = client.collections.items.upsert(
            collection_id="collection_id",
            identifiers={
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ]
            },
            values={
                "name": {
                    "data": "Aperture Science",
                    "type": "value/text/single_line",
                },
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ],
                "linked_in": {
                    "data": {},
                    "type": "value/uri/social_linked_in",
                },
            },
        )
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    def test_method_upsert_with_all_params(self, client: Moonbase) -> None:
        item = client.collections.items.upsert(
            collection_id="collection_id",
            identifiers={
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ]
            },
            values={
                "name": {
                    "data": "Aperture Science",
                    "type": "value/text/single_line",
                },
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ],
                "linked_in": {
                    "data": {
                        "url": "https://linkedin.com/company/aperturescience",
                        "username": "company/moonbaseai",
                    },
                    "type": "value/uri/social_linked_in",
                },
            },
            update_many_strategy="replace",
            update_one_strategy="replace",
        )
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    def test_raw_response_upsert(self, client: Moonbase) -> None:
        response = client.collections.items.with_raw_response.upsert(
            collection_id="collection_id",
            identifiers={
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ]
            },
            values={
                "name": {
                    "data": "Aperture Science",
                    "type": "value/text/single_line",
                },
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ],
                "linked_in": {
                    "data": {},
                    "type": "value/uri/social_linked_in",
                },
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = response.parse()
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    def test_streaming_response_upsert(self, client: Moonbase) -> None:
        with client.collections.items.with_streaming_response.upsert(
            collection_id="collection_id",
            identifiers={
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ]
            },
            values={
                "name": {
                    "data": "Aperture Science",
                    "type": "value/text/single_line",
                },
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ],
                "linked_in": {
                    "data": {},
                    "type": "value/uri/social_linked_in",
                },
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = response.parse()
            assert_matches_type(Item, item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_upsert(self, client: Moonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `collection_id` but received ''"):
            client.collections.items.with_raw_response.upsert(
                collection_id="",
                identifiers={
                    "domain": [
                        {
                            "data": "aperturescience.com",
                            "type": "value/uri/domain",
                        }
                    ]
                },
                values={
                    "name": {
                        "data": "Aperture Science",
                        "type": "value/text/single_line",
                    },
                    "domain": [
                        {
                            "data": "aperturescience.com",
                            "type": "value/uri/domain",
                        }
                    ],
                    "linked_in": {
                        "data": {},
                        "type": "value/uri/social_linked_in",
                    },
                },
            )


class TestAsyncItems:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncMoonbase) -> None:
        item = await async_client.collections.items.create(
            collection_id="collection_id",
            values={
                "name": {
                    "data": "Aperture Science",
                    "type": "value/text/single_line",
                },
                "ceo": {
                    "data": {
                        "id": "1CLJt2v2rARKGD4MLziBCw",
                        "type": "item",
                    },
                    "type": "value/relation",
                },
            },
        )
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.collections.items.with_raw_response.create(
            collection_id="collection_id",
            values={
                "name": {
                    "data": "Aperture Science",
                    "type": "value/text/single_line",
                },
                "ceo": {
                    "data": {
                        "id": "1CLJt2v2rARKGD4MLziBCw",
                        "type": "item",
                    },
                    "type": "value/relation",
                },
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = await response.parse()
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMoonbase) -> None:
        async with async_client.collections.items.with_streaming_response.create(
            collection_id="collection_id",
            values={
                "name": {
                    "data": "Aperture Science",
                    "type": "value/text/single_line",
                },
                "ceo": {
                    "data": {
                        "id": "1CLJt2v2rARKGD4MLziBCw",
                        "type": "item",
                    },
                    "type": "value/relation",
                },
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = await response.parse()
            assert_matches_type(Item, item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncMoonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `collection_id` but received ''"):
            await async_client.collections.items.with_raw_response.create(
                collection_id="",
                values={
                    "name": {
                        "data": "Aperture Science",
                        "type": "value/text/single_line",
                    },
                    "ceo": {
                        "data": {
                            "id": "1CLJt2v2rARKGD4MLziBCw",
                            "type": "item",
                        },
                        "type": "value/relation",
                    },
                },
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMoonbase) -> None:
        item = await async_client.collections.items.retrieve(
            id="id",
            collection_id="collection_id",
        )
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.collections.items.with_raw_response.retrieve(
            id="id",
            collection_id="collection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = await response.parse()
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMoonbase) -> None:
        async with async_client.collections.items.with_streaming_response.retrieve(
            id="id",
            collection_id="collection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = await response.parse()
            assert_matches_type(Item, item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncMoonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `collection_id` but received ''"):
            await async_client.collections.items.with_raw_response.retrieve(
                id="id",
                collection_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.collections.items.with_raw_response.retrieve(
                id="",
                collection_id="collection_id",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncMoonbase) -> None:
        item = await async_client.collections.items.update(
            id="id",
            collection_id="collection_id",
            values={
                "name": {
                    "data": "Jony Appleseed",
                    "type": "value/text/single_line",
                }
            },
        )
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMoonbase) -> None:
        item = await async_client.collections.items.update(
            id="id",
            collection_id="collection_id",
            values={
                "name": {
                    "data": "Jony Appleseed",
                    "type": "value/text/single_line",
                }
            },
            update_many_strategy="replace",
            update_one_strategy="replace",
        )
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.collections.items.with_raw_response.update(
            id="id",
            collection_id="collection_id",
            values={
                "name": {
                    "data": "Jony Appleseed",
                    "type": "value/text/single_line",
                }
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = await response.parse()
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMoonbase) -> None:
        async with async_client.collections.items.with_streaming_response.update(
            id="id",
            collection_id="collection_id",
            values={
                "name": {
                    "data": "Jony Appleseed",
                    "type": "value/text/single_line",
                }
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = await response.parse()
            assert_matches_type(Item, item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncMoonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `collection_id` but received ''"):
            await async_client.collections.items.with_raw_response.update(
                id="id",
                collection_id="",
                values={
                    "name": {
                        "data": "Jony Appleseed",
                        "type": "value/text/single_line",
                    }
                },
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.collections.items.with_raw_response.update(
                id="",
                collection_id="collection_id",
                values={
                    "name": {
                        "data": "Jony Appleseed",
                        "type": "value/text/single_line",
                    }
                },
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncMoonbase) -> None:
        item = await async_client.collections.items.list(
            collection_id="collection_id",
        )
        assert_matches_type(AsyncCursorPage[Item], item, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncMoonbase) -> None:
        item = await async_client.collections.items.list(
            collection_id="collection_id",
            after="after",
            before="before",
            limit=1,
        )
        assert_matches_type(AsyncCursorPage[Item], item, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.collections.items.with_raw_response.list(
            collection_id="collection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = await response.parse()
        assert_matches_type(AsyncCursorPage[Item], item, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncMoonbase) -> None:
        async with async_client.collections.items.with_streaming_response.list(
            collection_id="collection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = await response.parse()
            assert_matches_type(AsyncCursorPage[Item], item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncMoonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `collection_id` but received ''"):
            await async_client.collections.items.with_raw_response.list(
                collection_id="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncMoonbase) -> None:
        item = await async_client.collections.items.delete(
            id="id",
            collection_id="collection_id",
        )
        assert item is None

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.collections.items.with_raw_response.delete(
            id="id",
            collection_id="collection_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = await response.parse()
        assert item is None

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMoonbase) -> None:
        async with async_client.collections.items.with_streaming_response.delete(
            id="id",
            collection_id="collection_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = await response.parse()
            assert item is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMoonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `collection_id` but received ''"):
            await async_client.collections.items.with_raw_response.delete(
                id="id",
                collection_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.collections.items.with_raw_response.delete(
                id="",
                collection_id="collection_id",
            )

    @parametrize
    async def test_method_upsert(self, async_client: AsyncMoonbase) -> None:
        item = await async_client.collections.items.upsert(
            collection_id="collection_id",
            identifiers={
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ]
            },
            values={
                "name": {
                    "data": "Aperture Science",
                    "type": "value/text/single_line",
                },
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ],
                "linked_in": {
                    "data": {},
                    "type": "value/uri/social_linked_in",
                },
            },
        )
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    async def test_method_upsert_with_all_params(self, async_client: AsyncMoonbase) -> None:
        item = await async_client.collections.items.upsert(
            collection_id="collection_id",
            identifiers={
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ]
            },
            values={
                "name": {
                    "data": "Aperture Science",
                    "type": "value/text/single_line",
                },
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ],
                "linked_in": {
                    "data": {
                        "url": "https://linkedin.com/company/aperturescience",
                        "username": "company/moonbaseai",
                    },
                    "type": "value/uri/social_linked_in",
                },
            },
            update_many_strategy="replace",
            update_one_strategy="replace",
        )
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    async def test_raw_response_upsert(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.collections.items.with_raw_response.upsert(
            collection_id="collection_id",
            identifiers={
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ]
            },
            values={
                "name": {
                    "data": "Aperture Science",
                    "type": "value/text/single_line",
                },
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ],
                "linked_in": {
                    "data": {},
                    "type": "value/uri/social_linked_in",
                },
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = await response.parse()
        assert_matches_type(Item, item, path=["response"])

    @parametrize
    async def test_streaming_response_upsert(self, async_client: AsyncMoonbase) -> None:
        async with async_client.collections.items.with_streaming_response.upsert(
            collection_id="collection_id",
            identifiers={
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ]
            },
            values={
                "name": {
                    "data": "Aperture Science",
                    "type": "value/text/single_line",
                },
                "domain": [
                    {
                        "data": "aperturescience.com",
                        "type": "value/uri/domain",
                    }
                ],
                "linked_in": {
                    "data": {},
                    "type": "value/uri/social_linked_in",
                },
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = await response.parse()
            assert_matches_type(Item, item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_upsert(self, async_client: AsyncMoonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `collection_id` but received ''"):
            await async_client.collections.items.with_raw_response.upsert(
                collection_id="",
                identifiers={
                    "domain": [
                        {
                            "data": "aperturescience.com",
                            "type": "value/uri/domain",
                        }
                    ]
                },
                values={
                    "name": {
                        "data": "Aperture Science",
                        "type": "value/text/single_line",
                    },
                    "domain": [
                        {
                            "data": "aperturescience.com",
                            "type": "value/uri/domain",
                        }
                    ],
                    "linked_in": {
                        "data": {},
                        "type": "value/uri/social_linked_in",
                    },
                },
            )
