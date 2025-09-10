# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["InboxConversationListParams", "Filter", "FilterConversationID", "FilterInboxID"]


class InboxConversationListParams(TypedDict, total=False):
    after: str
    """
    When specified, returns results starting immediately after the item identified
    by this cursor. Use the cursor value from the previous response's metadata to
    fetch the next page of results.
    """

    before: str
    """
    When specified, returns results starting immediately before the item identified
    by this cursor. Use the cursor value from the response's metadata to fetch the
    previous page of results.
    """

    filter: Filter

    include: List[Literal["inbox", "messages", "messages.addresses"]]
    """Specifies which related objects to include in the response.

    Valid options are `inbox`, `messages`, and `messages.addresses`.
    """

    limit: int
    """Maximum number of items to return per page.

    Must be between 1 and 100. Defaults to 20 if not specified.
    """


class FilterConversationID(TypedDict, total=False):
    eq: str


class FilterInboxID(TypedDict, total=False):
    eq: str


class Filter(TypedDict, total=False):
    conversation_id: FilterConversationID

    inbox_id: FilterInboxID
