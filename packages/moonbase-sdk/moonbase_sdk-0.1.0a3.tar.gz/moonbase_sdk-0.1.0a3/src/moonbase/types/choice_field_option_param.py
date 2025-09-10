# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ChoiceFieldOptionParam"]


class ChoiceFieldOptionParam(TypedDict, total=False):
    id: Required[str]
    """Unique identifier for the option."""

    label: Required[str]
    """The human-readable text displayed for this option."""

    type: Required[Literal["choice_field_option"]]
    """String representing the object’s type.

    Always `choice_field_option` for this object.
    """
