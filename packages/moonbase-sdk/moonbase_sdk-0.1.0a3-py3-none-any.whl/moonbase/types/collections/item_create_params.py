# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Required, TypedDict

from ..field_value_param import FieldValueParam

__all__ = ["ItemCreateParams"]


class ItemCreateParams(TypedDict, total=False):
    values: Required[Dict[str, Optional[FieldValueParam]]]
    """A hash where keys are the `ref` of a `Field` and values are the data to be set."""
