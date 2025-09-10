# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .funnel import Funnel
from .._models import BaseModel

__all__ = ["StageField"]


class StageField(BaseModel):
    id: str
    """Unique identifier for the object."""

    cardinality: Literal["one", "many"]
    """
    Specifies whether the field can hold a single value (`one`) or multiple values
    (`many`).
    """

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    funnel: Funnel
    """The `Funnel` object that defines the available stages for this field."""

    name: str
    """The human-readable name of the field (e.g., "Sales Stage")."""

    readonly: bool
    """
    If `true`, the value of this field is system-managed and cannot be updated via
    the API.
    """

    ref: str
    """
    A unique, stable, machine-readable identifier for the field within its
    collection (e.g., `sales_stage`).
    """

    required: bool
    """If `true`, this field must have a value."""

    type: Literal["field/stage"]
    """The data type of the field. Always `field/stage` for this field."""

    unique: bool
    """
    If `true`, values for this field must be unique across all items in the
    collection.
    """

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""

    description: Optional[str] = None
    """An optional, longer-form description of the field's purpose."""
