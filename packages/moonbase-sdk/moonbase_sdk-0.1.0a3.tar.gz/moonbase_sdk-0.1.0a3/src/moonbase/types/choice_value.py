# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel
from .choice_field_option import ChoiceFieldOption

__all__ = ["ChoiceValue"]


class ChoiceValue(BaseModel):
    data: ChoiceFieldOption
    """An option that must match one of the predefined options for the field."""

    type: Literal["value/choice"]
