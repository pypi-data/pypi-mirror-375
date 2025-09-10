# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["CollectionPointerParam"]


class CollectionPointerParam(TypedDict, total=False):
    id: Required[str]
    """Unique identifier of the collection."""

    ref: Required[str]
    """The stable, machine-readable reference identifier of the collection."""

    type: Required[Literal["collection"]]
    """String representing the object’s type. Always `collection` for this object."""
