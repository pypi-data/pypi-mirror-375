# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel
from .item_pointer import ItemPointer

__all__ = ["RelationValue"]


class RelationValue(BaseModel):
    data: ItemPointer
    """A reference to another Moonbase item."""

    type: Literal["value/relation"]
