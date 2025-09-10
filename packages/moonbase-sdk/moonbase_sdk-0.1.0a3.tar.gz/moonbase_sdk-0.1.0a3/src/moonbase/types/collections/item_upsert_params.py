# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from ..field_value_param import FieldValueParam

__all__ = ["ItemUpsertParams"]


class ItemUpsertParams(TypedDict, total=False):
    identifiers: Required[Dict[str, Optional[FieldValueParam]]]
    """
    A hash where keys are the `ref` of a `Field` and values are used to identify the
    item to update. When multiple identifiers are provided, the update will find
    items that match any of the identifiers.
    """

    values: Required[Dict[str, Optional[FieldValueParam]]]
    """A hash where keys are the `ref` of a `Field` and values are the data to be set."""

    update_many_strategy: Annotated[Literal["replace", "preserve", "merge"], PropertyInfo(alias="update-many-strategy")]

    update_one_strategy: Annotated[Literal["replace", "preserve"], PropertyInfo(alias="update-one-strategy")]
