# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["InboxConversationRetrieveParams"]


class InboxConversationRetrieveParams(TypedDict, total=False):
    include: List[Literal["inbox", "messages", "messages.addresses"]]
    """Specifies which related objects to include in the response.

    Valid options are `inbox`, `messages`, and `messages.addresses`.
    """
