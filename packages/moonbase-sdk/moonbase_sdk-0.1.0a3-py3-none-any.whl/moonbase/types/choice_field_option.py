# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ChoiceFieldOption"]


class ChoiceFieldOption(BaseModel):
    id: str
    """Unique identifier for the option."""

    label: str
    """The human-readable text displayed for this option."""

    type: Literal["choice_field_option"]
    """String representing the object’s type.

    Always `choice_field_option` for this object.
    """
