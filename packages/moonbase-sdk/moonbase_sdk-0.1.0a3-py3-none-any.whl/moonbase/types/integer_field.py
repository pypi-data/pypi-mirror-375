# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["IntegerField"]


class IntegerField(BaseModel):
    id: str
    """Unique identifier for the object."""

    cardinality: Literal["one", "many"]
    """
    Specifies whether the field can hold a single value (`one`) or multiple values
    (`many`).
    """

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    name: str
    """The human-readable name of the field (e.g., "Employee Count")."""

    readonly: bool
    """
    If `true`, the value of this field is system-managed and cannot be updated via
    the API.
    """

    ref: str
    """
    A unique, stable, machine-readable identifier for the field within its
    collection (e.g., `employee_count`).
    """

    required: bool
    """If `true`, this field must have a value."""

    type: Literal["field/number/unitless_integer"]
    """The data type of the field.

    Always `field/number/unitless_integer` for this field.
    """

    unique: bool
    """
    If `true`, values for this field must be unique across all items in the
    collection.
    """

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""

    description: Optional[str] = None
    """An optional, longer-form description of the field's purpose."""
