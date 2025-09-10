# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["Pointer"]


class Pointer(TypedDict, total=False):
    id: Required[str]
    """Unique identifier for the referenced object."""

    type: Required[str]
    """String indicating the type of the referenced object."""
