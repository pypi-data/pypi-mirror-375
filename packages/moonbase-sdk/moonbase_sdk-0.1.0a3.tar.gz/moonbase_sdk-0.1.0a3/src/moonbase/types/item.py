# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict
from typing_extensions import Literal

from .._models import BaseModel
from .field_value import FieldValue

__all__ = ["Item"]


class Item(BaseModel):
    id: str
    """Unique identifier for the object."""

    type: Literal["item"]
    """String representing the object’s type. Always `item` for this object."""

    values: Dict[str, FieldValue]
    """
    A hash where keys are the `ref` of a `Field` and values are the data stored for
    that field.
    """
