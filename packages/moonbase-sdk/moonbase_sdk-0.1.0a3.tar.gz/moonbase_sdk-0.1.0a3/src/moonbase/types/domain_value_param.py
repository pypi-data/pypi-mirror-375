# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["DomainValueParam"]


class DomainValueParam(TypedDict, total=False):
    data: Required[str]
    """A valid internet domain name, without protocol (e.g., 'https://') or path."""

    type: Required[Literal["value/uri/domain"]]
