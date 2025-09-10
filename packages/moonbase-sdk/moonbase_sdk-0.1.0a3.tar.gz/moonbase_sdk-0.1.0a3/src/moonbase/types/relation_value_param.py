# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .item_pointer_param import ItemPointerParam
from .shared_params.pointer import Pointer

__all__ = ["RelationValueParam", "Data"]

Data: TypeAlias = Union[ItemPointerParam, Pointer]


class RelationValueParam(TypedDict, total=False):
    data: Required[Data]
    """A reference to another Moonbase item."""

    type: Required[Literal["value/relation"]]
