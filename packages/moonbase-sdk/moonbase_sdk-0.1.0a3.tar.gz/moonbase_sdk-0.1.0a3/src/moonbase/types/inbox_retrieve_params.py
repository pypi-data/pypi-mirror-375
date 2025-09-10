# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["InboxRetrieveParams"]


class InboxRetrieveParams(TypedDict, total=False):
    include: Annotated[Literal["tagset"], PropertyInfo(alias="include[]")]
    """Specifies which related objects to include in the response.

    Valid option is `tagset`.
    """
