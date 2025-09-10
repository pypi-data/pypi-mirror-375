# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .shared_params.pointer import Pointer
from .choice_field_option_param import ChoiceFieldOptionParam

__all__ = ["ChoiceValueParam", "Data"]

Data: TypeAlias = Union[ChoiceFieldOptionParam, Pointer]


class ChoiceValueParam(TypedDict, total=False):
    data: Required[Data]
    """An option that must match one of the predefined options for the field."""

    type: Required[Literal["value/choice"]]
